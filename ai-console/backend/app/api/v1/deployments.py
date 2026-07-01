import asyncio
import logging
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.async_tasks import async_task_manager
from app.core.config import settings
from app.core.database import AsyncSessionLocal, get_db
from app.models.deployment import Deployment
from app.models.deployment_device import DeploymentDevice
from app.models.device import Device
from app.schemas.request.deployment import (
    DeploymentRequest,
    DeploymentResponse,
    DeploymentStartRequest,
)
from app.services.process_monitor import ProcessMonitor
from app.services.stream_url_resolver import resolve_stream_url_for_device
from app.services.traffic_api_client import (
    TrafficApiAuthError,
    TrafficApiConflictError,
    TrafficApiNotFoundError,
    TrafficApiResourceError,
    TrafficApiServerError,
    TrafficApiUnavailableError,
    get_traffic_api_client,
)

router = APIRouter(prefix="/deployments", tags=["deployments"])

# In-memory store for async restart-all tasks. Keyed by task_id.
_restart_all_tasks: dict[str, dict[str, Any]] = {}
_restart_all_lock = asyncio.Lock()

# How long terminal tasks remain queryable (seconds).
_COMPLETED_TASK_TTL_SECONDS = 3600

# Polling interval for traffic-api restart-all status (seconds).
_RESTART_ALL_POLL_INTERVAL_SECONDS = 2.0

# Hard cap on how long we'll poll a single traffic-api task (seconds).
# Prevents leaked polling loops when traffic-api never reaches a terminal state.
_RESTART_ALL_POLL_TIMEOUT_SECONDS = 1800


def _prune_completed_tasks() -> None:
    """Remove old terminal tasks to keep the in-memory store bounded."""
    now = time.monotonic()
    stale_keys = [
        task_id
        for task_id, info in list(_restart_all_tasks.items())
        if info.get("status") in ("completed", "failed")
        and now - info.get("completed_at", now) > _COMPLETED_TASK_TTL_SECONDS
    ]
    for task_id in stale_keys:
        del _restart_all_tasks[task_id]


async def _set_task_state(
    task_id: str,
    status: str,
    extra: Optional[dict[str, Any]] = None,
) -> None:
    """Atomic, lock-protected update of a restart-all task's state."""
    async with _restart_all_lock:
        task_info = _restart_all_tasks.get(task_id)
        if task_info is None:
            return
        task_info["status"] = status
        if extra:
            task_info.update(extra)
        if status in ("completed", "failed"):
            task_info["completed_at"] = time.monotonic()


async def _run_restart_all_task(task_id: str) -> None:
    """Execute restart-all in a background task with a fresh DB session."""
    async with AsyncSessionLocal() as db:
        try:
            await _execute_restart_all_deployments(task_id, db)
        except Exception as exc:
            logging.exception("Restart-all task %s failed", task_id)
            await _set_task_state(task_id, "failed", {"error": str(exc)})


async def _execute_restart_all_deployments(
    task_id: str,
    db: AsyncSession,
) -> None:
    """透传到 traffic-api POST /api/v1/deployments/restart-all。

    进度字段 total/restarted/failed/skipped/errors[] 由 traffic-api 直接返回
    （API_SERVICE(1).md:501-512），本地只负责状态分发与最终汇总。
    """
    await _set_task_state(task_id, "running")

    result = await db.execute(select(Deployment).where(Deployment.deleted_at.is_(None)))
    deployments = result.scalars().all()
    deployment_ids = [d.id for d in deployments if d.algorithm_id and d.module_name]

    await _set_task_state(task_id, "running", {"total": len(deployment_ids)})

    client = get_traffic_api_client()
    try:
        # 一次性透传：traffic-api 内部负责逐个 stop+start（间隔避免 GPU 抢占）。
        api_result = await client.restart_all(deployment_ids=deployment_ids or None)
    except (TrafficApiUnavailableError, TrafficApiAuthError, TrafficApiServerError) as exc:
        await _set_task_state(
            task_id,
            "failed",
            {"error": str(exc), "errors": [{"error": str(exc)}]},
        )
        return

    # traffic-api 返回的 task_id 缓存为子任务，便于前端轮询（前端沿用本地 task_id）。
    sub_task_id = api_result.get("task_id") if isinstance(api_result, dict) else None

    # traffic-api 同步返回的初始进度（可能为 0，因为真正的工作仍在异步执行）。
    initial_restarted = int(api_result.get("restarted", 0)) if isinstance(api_result, dict) else 0
    initial_failed = int(api_result.get("failed", 0)) if isinstance(api_result, dict) else 0
    initial_skipped = int(api_result.get("skipped", 0)) if isinstance(api_result, dict) else 0
    initial_errors: list[dict[str, Any]] = (
        list(api_result.get("errors", [])) if isinstance(api_result, dict) else []
    )

    # 先发布初始进度 + traffic_api_task_id，task 保持 running。
    await _set_task_state(
        task_id,
        "running",
        {
            "total": len(deployment_ids),
            "restarted": initial_restarted,
            "failed": initial_failed,
            "skipped": initial_skipped,
            "errors": initial_errors,
            "traffic_api_task_id": sub_task_id,
        },
    )

    if not sub_task_id:
        # 兜底：traffic-api 没有返回 task_id，视为同步完成。
        await _set_task_state(task_id, "completed")
        return

    # 进入轮询：traffic-api 的 restart-all 是异步任务，需等待其真正完成。
    client = get_traffic_api_client()
    deadline = time.monotonic() + _RESTART_ALL_POLL_TIMEOUT_SECONDS
    while True:
        await asyncio.sleep(_RESTART_ALL_POLL_INTERVAL_SECONDS)
        if time.monotonic() > deadline:
            await _set_task_state(
                task_id,
                "failed",
                {"error": f"traffic-api 任务轮询超时（>{_RESTART_ALL_POLL_TIMEOUT_SECONDS}s）"},
            )
            return
        try:
            poll = await client.restart_all_status(sub_task_id)
        except (TrafficApiUnavailableError, TrafficApiAuthError, TrafficApiServerError) as exc:
            await _set_task_state(
                task_id,
                "failed",
                {"error": f"traffic-api 状态查询失败: {exc}"},
            )
            return

        if not isinstance(poll, dict):
            continue
        # 透传最新进度
        progress_extra: dict[str, Any] = {
            "traffic_api_task_id": sub_task_id,
            "total": len(deployment_ids),
            "restarted": int(poll.get("restarted", initial_restarted) or 0),
            "failed": int(poll.get("failed", initial_failed) or 0),
            "skipped": int(poll.get("skipped", initial_skipped) or 0),
            "errors": list(poll.get("errors", initial_errors) or []),
        }
        traffic_status = (poll.get("status") or "").lower()
        if traffic_status in ("completed", "succeeded", "done"):
            await _set_task_state(task_id, "completed", progress_extra)
            return
        if traffic_status in ("failed", "error", "cancelled", "canceled"):
            await _set_task_state(
                task_id,
                "failed",
                {**progress_extra, "error": poll.get("error") or "traffic-api 任务失败"},
            )
            return
        # 仍进行中：发布最新进度
        await _set_task_state(task_id, "running", progress_extra)


@router.post("/restart-all", response_model=dict)
async def restart_all_deployments() -> dict:
    """Start an asynchronous task that restarts all deployments.

    Returns immediately with a task_id that can be polled via
    GET /deployments/restart-all/status/{task_id}.
    """
    task_id = str(uuid.uuid4())
    _restart_all_tasks[task_id] = {
        "status": "pending",
        "total": 0,
        "restarted": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "error": None,
        "completed_at": None,
    }
    _prune_completed_tasks()
    asyncio.create_task(_run_restart_all_task(task_id))
    return {"task_id": task_id, "status": "pending"}


@router.get("/restart-all/status/{task_id}", response_model=dict)
async def get_restart_all_status(task_id: str) -> dict:
    """Poll the status of an asynchronous restart-all task."""
    async with _restart_all_lock:
        task = _restart_all_tasks.get(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="任务不存在")
        return dict(task)


async def _get_deployment_or_404(db: AsyncSession, item_id: int) -> Deployment:
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")
    return deployment


async def _get_device_ids_map(db: AsyncSession, deployment_ids: list[int]) -> dict[int, list[int]]:
    """批量查询 deployment 的关联设备 ID"""
    if not deployment_ids:
        return {}
    stmt = select(DeploymentDevice.deployment_id, DeploymentDevice.device_id).where(
        DeploymentDevice.deployment_id.in_(deployment_ids)
    )
    result = await db.execute(stmt)
    mapping: dict[int, list[int]] = {}
    for dep_id, dev_id in result.all():
        mapping.setdefault(dep_id, []).append(dev_id)
    return mapping


def _build_response(item: Deployment, device_ids: list[int]) -> dict:
    """构建包含 device_ids 的响应字典"""
    return {
        "id": item.id,
        "name": item.name,
        "algorithm_id": item.algorithm_id,
        "service_id": item.service_id,
        "status": item.status,
        "algorithm_status": item.algorithm_status,
        "deployed_at": item.deployed_at,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "deleted_at": item.deleted_at,
        "device_ids": device_ids,
        "schedule": item.schedule,
        "pid": item.pid,
        "config_json": item.config_json,
        "started_at": item.started_at,
        "stopped_at": item.stopped_at,
        "exit_code": item.exit_code,
        "log_path": item.log_path,
        "module_name": item.module_name,
        "org_id": item.org_id,
        "region_id": item.region_id,
    }


async def _get_devices_for_deployment(db: AsyncSession, deployment_id: int) -> list[Device]:
    stmt = (
        select(Device)
        .join(DeploymentDevice, DeploymentDevice.device_id == Device.id)
        .where(DeploymentDevice.deployment_id == deployment_id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("", response_model=dict)
async def list_deployments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    algorithm_id: Optional[int] = Query(None),
    device_id: Optional[int] = Query(None),
    module_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Deployment).where(Deployment.deleted_at.is_(None))

    if keyword:
        query = query.where(Deployment.name.ilike(f"%{keyword}%"))
    if status:
        query = query.where(Deployment.status == status)
    if algorithm_id:
        query = query.where(Deployment.algorithm_id == algorithm_id)
    if device_id:
        query = (
            query.join(DeploymentDevice, Deployment.id == DeploymentDevice.deployment_id)
            .where(DeploymentDevice.device_id == device_id)
        )
    if module_name:
        query = query.where(Deployment.module_name == module_name)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # 批量查询关联设备
    dep_ids = [item.id for item in items]
    device_map = await _get_device_ids_map(db, dep_ids)

    return {
        "items": [DeploymentResponse.model_validate(_build_response(item, device_map.get(item.id, []))) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=DeploymentResponse)
async def get_deployment(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    device_map = await _get_device_ids_map(db, [deployment.id])
    return DeploymentResponse.model_validate(_build_response(deployment, device_map.get(deployment.id, [])))


@router.post("", response_model=DeploymentResponse)
async def create_deployment(data: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    device_ids = data.device_ids or []

    # 创建 Deployment（排除 device_ids）
    dump = data.model_dump(exclude={"device_ids"})
    if not dump.get("name"):
        raise HTTPException(status_code=400, detail="name is required")
    deployment = Deployment(**dump)
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)

    # 批量插入关联
    if device_ids:
        db.add_all([
            DeploymentDevice(deployment_id=deployment.id, device_id=did)
            for did in device_ids
        ])
        await db.commit()

    return DeploymentResponse.model_validate(_build_response(deployment, device_ids))


@router.put("/{item_id}", response_model=DeploymentResponse)
async def update_deployment(item_id: int, data: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    device_ids = data.device_ids or []

    # 更新 Deployment 字段（排除 device_ids，只更新请求中发送的字段）
    for key, value in data.model_dump(exclude={"device_ids"}, exclude_unset=True).items():
        setattr(deployment, key, value)

    await db.commit()
    await db.refresh(deployment)

    # 删除旧关联，插入新关联
    await db.execute(delete(DeploymentDevice).where(DeploymentDevice.deployment_id == item_id))
    if device_ids:
        db.add_all([
            DeploymentDevice(deployment_id=item_id, device_id=did)
            for did in device_ids
        ])
    await db.commit()

    return DeploymentResponse.model_validate(_build_response(deployment, device_ids))


@router.delete("/{item_id}")
async def delete_deployment(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.deleted_at = datetime.utcnow()

    # 硬删除关联
    await db.execute(delete(DeploymentDevice).where(DeploymentDevice.deployment_id == item_id))
    await db.commit()

    return {"message": "Deployment deleted"}


async def _resolve_stream_id_and_device(
    devices: list[Device],
    stream_map: Optional[dict[int, str] | dict[str, str]],
) -> tuple[str, Device]:
    if not devices:
        raise HTTPException(status_code=400, detail="Deployment has no associated devices")

    if len(devices) > 1 and not stream_map:
        raise HTTPException(
            status_code=400,
            detail="stream_map is required when deployment targets multiple devices",
        )

    primary_device = devices[0]
    if stream_map:
        # JSON serialization turns integer keys into strings; normalize to str for lookup.
        normalized_map = {str(k): v for k, v in stream_map.items()}
        device_key = str(primary_device.id)
        if device_key not in normalized_map:
            raise HTTPException(
                status_code=400,
                detail=f"stream_map missing entry for device {primary_device.id}",
            )
        stream_id = normalized_map[device_key]
    else:
        stream_id = str(primary_device.id)

    return stream_id, primary_device


async def _fill_org_region_from_devices(deployment: Deployment, devices: list[Device]) -> None:
    first = devices[0]
    if any(d.org_id != first.org_id or d.region_id != first.region_id for d in devices[1:]):
        raise HTTPException(
            status_code=400,
            detail="All devices in a deployment must share the same org_id and region_id",
        )
    deployment.org_id = first.org_id
    deployment.region_id = first.region_id


@router.post("/{item_id}/start", response_model=dict)
async def start_deployment(
    item_id: int,
    data: DeploymentStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """启动 deployment，立即返回 task_id，由后台完成 ProcessMonitor.start()。"""
    deployment = await _get_deployment_or_404(db, item_id)
    if not deployment.algorithm_id:
        raise HTTPException(status_code=400, detail="Deployment has no associated algorithm")

    task_id = async_task_manager.create_task(
        status="pending",
        extra={"deployment_id": item_id, "action": "start"},
    )
    async_task_manager.run_task(
        task_id,
        lambda tid: _run_deployment_start_task(tid, item_id, data.model_dump()),
    )
    return {"task_id": task_id, "status": "pending"}


@router.get("/{item_id}/start/status/{task_id}", response_model=dict)
async def get_start_deployment_status(task_id: str):
    """查询 deployment 启动任务状态。"""
    task = await async_task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


async def _run_deployment_start_task(
    task_id: str,
    item_id: int,
    data: dict[str, Any],
) -> None:
    """后台执行 deployment 启动并更新任务状态（traffic-api 化）。"""
    await async_task_manager.update_task(task_id, "running")

    try:
        async with AsyncSessionLocal() as db:
            deployment = await _get_deployment_or_404(db, item_id)
            devices = await _get_devices_for_deployment(db, item_id)

            stream_map = data.get("stream_map")
            stream_id, primary_device = await _resolve_stream_id_and_device(devices, stream_map)
            await _fill_org_region_from_devices(deployment, devices)

            video_path = data.get("video_path") or ""
            if not video_path or video_path.strip().lower() == "auto":
                if primary_device is None:
                    raise ValueError("Deployment has no associated devices")
                resolved = await resolve_stream_url_for_device(db, primary_device.id)
                if not resolved:
                    raise ValueError(
                        f"无法为设备 {primary_device.id} 自动解析流地址，请显式提供 video_path"
                    )
                video_path = resolved

            module_config = dict(data.get("config") or {})
            log_path = data.get("log_path") or str(
                Path(__file__).resolve().parents[3] / "logs" / f"traffic_{deployment.id}.log"
            )

            deployment.module_name = data.get("module_name")
            deployment.config_json = {
                "stream_map": stream_map,
                "module_config": module_config,
                "video_path": video_path,
            }
            # callback_url 默认从 settings 注入（SSRF 防护要求公网；本地开发可空字符串）
            module_config.setdefault("callback_url", settings.TRAFFIC_API_DEFAULT_CALLBACK_URL)
            module_config.setdefault("push_interval", 1.0)

            await db.commit()

            client = get_traffic_api_client()
            payload = {
                "module_name": deployment.module_name,
                "video_path": video_path,
                "stream_map": stream_map or {str(primary_device.id): str(primary_device.id)},
                "config": module_config,
                "log_path": log_path,
            }
            result = await client.start(deployment.id, payload)

            # callback_token 复用 deployment_token 字段（String(64)；
            # traffic-api 文档示例 37 字符 "cbk_xxx"，有 27 字符 headroom）。
            # UPDATE 不冲突 unique 约束。traffic-api /status 返回的 pid 也写入。
            callback_token = result.get("callback_token") if isinstance(result, dict) else None
            traffic_task_id = result.get("task_id") if isinstance(result, dict) else None
            if callback_token:
                deployment.deployment_token = callback_token
            deployment.pid = result.get("pid") if isinstance(result, dict) else None
            deployment.log_path = result.get("log_path") or log_path
            deployment.started_at = datetime.utcnow()
            deployment.stopped_at = None
            deployment.exit_code = None
            deployment.algorithm_status = "running"

            await db.commit()
            await db.refresh(deployment)

            await async_task_manager.update_task(
                task_id,
                "completed",
                {
                    "deployment_id": deployment.id,
                    "algorithm_status": deployment.algorithm_status,
                    "pid": deployment.pid,
                    "deployment_token": deployment.deployment_token,
                    "traffic_api_task_id": traffic_task_id,
                },
            )
    except TrafficApiConflictError as exc:
        logging.warning("Deployment %s start conflict: %s", item_id, exc)
        await async_task_manager.update_task(task_id, "failed", {"error": str(exc)})
    except (TrafficApiResourceError, TrafficApiUnavailableError, TrafficApiServerError) as exc:
        logging.exception("Deployment start task %s failed (traffic-api)", task_id)
        await _mark_deployment_error(item_id, str(exc))
        await async_task_manager.update_task(task_id, "failed", {"error": str(exc)})
    except TrafficApiAuthError as exc:
        logging.exception("Deployment start task %s auth failed", task_id)
        await _mark_deployment_error(item_id, str(exc))
        await async_task_manager.update_task(task_id, "failed", {"error": str(exc)})
    except Exception as exc:
        logging.exception("Deployment start task %s failed", task_id)
        await _mark_deployment_error(item_id, str(exc))
        await async_task_manager.update_task(task_id, "failed", {"error": str(exc)})


async def _mark_deployment_error(item_id: int, reason: str) -> None:
    """把 deployment 标记为 error 状态（不抛异常）。"""
    try:
        async with AsyncSessionLocal() as db:
            deployment = await db.get(Deployment, item_id)
            if deployment is None:
                return
            deployment.algorithm_status = "error"
            deployment.stopped_at = datetime.utcnow()
            await db.commit()
    except Exception:
        logging.exception("Failed to mark deployment %s as error: %s", item_id, reason)


@router.post("/{item_id}/stop", response_model=dict)
async def stop_deployment(item_id: int, db: AsyncSession = Depends(get_db)):
    """停止 deployment，立即返回 task_id，由后台完成 ProcessMonitor.stop()。"""
    await _get_deployment_or_404(db, item_id)

    task_id = async_task_manager.create_task(
        status="pending",
        extra={"deployment_id": item_id, "action": "stop"},
    )
    async_task_manager.run_task(
        task_id,
        lambda tid: _run_deployment_stop_task(tid, item_id),
    )
    return {"task_id": task_id, "status": "pending"}


@router.get("/{item_id}/stop/status/{task_id}", response_model=dict)
async def get_stop_deployment_status(task_id: str):
    """查询 deployment 停止任务状态。"""
    task = await async_task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


async def _run_deployment_stop_task(task_id: str, item_id: int) -> None:
    """后台执行 deployment 停止并更新任务状态（traffic-api 化）。"""
    await async_task_manager.update_task(task_id, "running")

    try:
        async with AsyncSessionLocal() as db:
            deployment = await _get_deployment_or_404(db, item_id)
            client = get_traffic_api_client()
            try:
                stop_result = await client.stop(deployment.id)
            except TrafficApiNotFoundError:
                # traffic-api 重启后任务记录丢失（traffic-api 无持久化）：
                # 视为已停止，不当作错误。
                stop_result = {"exit_code": 0, "not_found": True}

            exit_code = stop_result.get("exit_code") if isinstance(stop_result, dict) else None
            deployment.stopped_at = datetime.utcnow()
            deployment.exit_code = exit_code
            deployment.pid = None
            deployment.algorithm_status = "stopped" if exit_code in (0, None) else "crashed"

            await db.commit()
            await db.refresh(deployment)

            await async_task_manager.update_task(
                task_id,
                "completed",
                {
                    "deployment_id": deployment.id,
                    "algorithm_status": deployment.algorithm_status,
                    "exit_code": deployment.exit_code,
                },
            )
    except (TrafficApiUnavailableError, TrafficApiServerError, TrafficApiAuthError) as exc:
        logging.exception("Deployment stop task %s failed (traffic-api)", task_id)
        await async_task_manager.update_task(
            task_id,
            "failed",
            {"error": str(exc)},
        )
    except Exception as exc:
        logging.exception("Deployment stop task %s failed", task_id)
        await async_task_manager.update_task(
            task_id,
            "failed",
            {"error": str(exc)},
        )



@router.get("/{item_id}/status", response_model=dict)
async def deployment_status(item_id: int, db: AsyncSession = Depends(get_db)):
    """透传 traffic-api /status：pid 来自 traffic-api，is_running 来自 status 枚举。"""
    deployment = await _get_deployment_or_404(db, item_id)
    client = get_traffic_api_client()

    traffic_status: dict[str, Any] | None = None
    try:
        traffic_status = await client.status(deployment.id)
    except TrafficApiNotFoundError:
        traffic_status = None

    is_running = False
    live_pid: int | None = None
    if traffic_status is not None:
        status_str = (traffic_status.get("status") or "").lower()
        is_running = status_str in {"pending", "running", "stopping"}
        live_pid = traffic_status.get("pid")
        # 状态同步：traffic-api 是真值源
        new_alg_status = _map_traffic_status(status_str, fallback=deployment.algorithm_status)
        if new_alg_status != deployment.algorithm_status:
            deployment.algorithm_status = new_alg_status
            if new_alg_status in {"stopped", "crashed", "completed", "unknown"}:
                deployment.stopped_at = datetime.utcnow()
                deployment.pid = None
            await db.commit()
            await db.refresh(deployment)
    elif deployment.algorithm_status == "running":
        # traffic-api 404：traffic-api 重启后任务记录丢失 → 标记 unknown
        deployment.algorithm_status = "unknown"
        deployment.pid = None
        await db.commit()
        await db.refresh(deployment)

    device_map = await _get_device_ids_map(db, [deployment.id])
    return {
        "deployment": DeploymentResponse.model_validate(
            _build_response(deployment, device_map.get(deployment.id, []))
        ),
        "is_running": is_running,
        "pid": live_pid if live_pid is not None else deployment.pid,
    }


def _map_traffic_status(traffic_status: str, *, fallback: str) -> str:
    """traffic-api status → Deployment.algorithm_status。"""
    if traffic_status == "running":
        return "running"
    if traffic_status in {"pending", "stopping"}:
        return "pending"
    if traffic_status == "stopped":
        return "stopped"
    if traffic_status == "crashed":
        return "crashed"
    if traffic_status == "completed":
        return "completed"
    return fallback
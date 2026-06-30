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

router = APIRouter(prefix="/deployments", tags=["deployments"])

# In-memory store for async restart-all tasks. Keyed by task_id.
_restart_all_tasks: dict[str, dict[str, Any]] = {}
_restart_all_lock = asyncio.Lock()

# How long terminal tasks remain queryable (seconds).
_COMPLETED_TASK_TTL_SECONDS = 3600


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
    """Stop and restart all non-deleted deployments, updating task progress."""
    await _set_task_state(task_id, "running")

    result = await db.execute(select(Deployment).where(Deployment.deleted_at.is_(None)))
    deployments = result.scalars().all()
    await _set_task_state(task_id, "running", {"total": len(deployments)})

    monitor = ProcessMonitor()
    restarted = 0
    failed = 0
    skipped = 0
    errors: list[dict[str, Any]] = []

    for deployment in deployments:
        if not deployment.algorithm_id or not deployment.module_name:
            skipped += 1
            continue

        devices = await _get_devices_for_deployment(db, deployment.id)
        if not devices:
            skipped += 1
            continue

        config_json = deployment.config_json or {}
        stream_map = config_json.get("stream_map") or {}
        try:
            stream_id, primary_device = await _resolve_stream_id_and_device(devices, stream_map)
        except HTTPException as exc:
            skipped += 1
            errors.append({"deployment_id": deployment.id, "error": f"stream_id: {exc.detail}"})
            continue

        try:
            await monitor.stop(deployment.id)
        except Exception as exc:
            logging.warning("Failed to stop deployment %s before restart: %s", deployment.id, exc)

        video_path = config_json.get("video_path")
        if not video_path or str(video_path).strip().lower() == "auto":
            video_path = await resolve_stream_url_for_device(db, primary_device.id)

        if not video_path:
            skipped += 1
            errors.append({"deployment_id": deployment.id, "error": "no video_path resolved"})
            continue

        module_config = dict(config_json.get("module_config") or {})
        log_path = deployment.log_path or str(
            Path(__file__).resolve().parents[3] / "logs" / f"traffic_{deployment.id}.log"
        )

        token = ProcessMonitor.generate_token()
        deployment.deployment_token = token
        deployment.config_json = {
            "stream_map": stream_map,
            "module_config": module_config,
            "video_path": video_path,
        }

        try:
            start_result = await monitor.start(
                module_name=deployment.module_name,
                video_path=video_path,
                deployment_id=deployment.id,
                stream_id=stream_id,
                config=module_config,
                log_path=log_path,
                deployment_token=token,
            )
        except Exception as exc:
            failed += 1
            errors.append({"deployment_id": deployment.id, "error": str(exc)})
            continue

        deployment.pid = start_result["pid"]
        deployment.log_path = start_result.get("log_path") or log_path
        deployment.started_at = datetime.utcnow()
        deployment.stopped_at = None
        deployment.exit_code = None
        deployment.algorithm_status = "running"
        await _fill_org_region_from_devices(deployment, devices)
        restarted += 1

        # Publish live progress after each deployment.
        await _set_task_state(
            task_id,
            "running",
            {
                "total": len(deployments),
                "restarted": restarted,
                "failed": failed,
                "skipped": skipped,
                "errors": list(errors),
            },
        )

    await db.commit()
    await _set_task_state(
        task_id,
        "completed",
        {
            "total": len(deployments),
            "restarted": restarted,
            "failed": failed,
            "skipped": skipped,
            "errors": list(errors),
        },
    )


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
    """后台执行 deployment 启动并更新任务状态。"""
    await async_task_manager.update_task(task_id, "running")

    try:
        async with AsyncSessionLocal() as db:
            deployment = await _get_deployment_or_404(db, item_id)
            devices = await _get_devices_for_deployment(db, item_id)

            stream_map = data.get("stream_map")
            stream_id, primary_device = await _resolve_stream_id_and_device(devices, stream_map)
            await _fill_org_region_from_devices(deployment, devices)

            monitor = ProcessMonitor()
            if monitor.is_deployment_running(deployment.id):
                raise RuntimeError("Deployment is already running")

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

            # Generate and persist the deployment token BEFORE forking so the
            # ingest endpoint can authenticate events from the very first frame.
            token = ProcessMonitor.generate_token()
            deployment.deployment_token = token
            deployment.module_name = data.get("module_name")
            deployment.config_json = {
                "stream_map": stream_map,
                "module_config": module_config,
                "video_path": video_path,
            }
            await db.commit()

            result = await monitor.start(
                module_name=data.get("module_name"),
                video_path=video_path,
                deployment_id=deployment.id,
                stream_id=stream_id,
                config=module_config,
                log_path=log_path,
                deployment_token=token,
            )

            deployment.pid = result["pid"]
            deployment.log_path = result["log_path"]
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
                },
            )
    except Exception as exc:
        logging.exception("Deployment start task %s failed", task_id)
        async with AsyncSessionLocal() as db:
            deployment = await db.get(Deployment, item_id)
            if deployment is not None:
                deployment.algorithm_status = "error"
                deployment.stopped_at = datetime.utcnow()
                try:
                    await db.commit()
                except Exception:
                    logging.exception("Failed to mark deployment %s as error", item_id)
        await async_task_manager.update_task(
            task_id,
            "failed",
            {"error": str(exc)},
        )


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
    """后台执行 deployment 停止并更新任务状态。"""
    await async_task_manager.update_task(task_id, "running")

    try:
        async with AsyncSessionLocal() as db:
            deployment = await _get_deployment_or_404(db, item_id)
            monitor = ProcessMonitor()
            stop_result = await monitor.stop(deployment.id)

            deployment.stopped_at = datetime.utcnow()
            deployment.exit_code = stop_result.get("exit_code")
            deployment.pid = None
            deployment.algorithm_status = "stopped" if stop_result.get("exit_code") == 0 else "crashed"

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
    except Exception as exc:
        logging.exception("Deployment stop task %s failed", task_id)
        await async_task_manager.update_task(
            task_id,
            "failed",
            {"error": str(exc)},
        )



@router.get("/{item_id}/status", response_model=dict)
async def deployment_status(item_id: int, db: AsyncSession = Depends(get_db)):
    deployment = await _get_deployment_or_404(db, item_id)
    monitor = ProcessMonitor()

    is_running = monitor.is_deployment_running(deployment.id)
    if not is_running and deployment.algorithm_status == "running":
        exit_code = monitor.get_exit_code(deployment.id)
        deployment.stopped_at = datetime.utcnow()
        deployment.exit_code = exit_code
        deployment.pid = None
        deployment.algorithm_status = "stopped" if exit_code == 0 else "crashed"
        await db.commit()
        await db.refresh(deployment)

    device_map = await _get_device_ids_map(db, [deployment.id])
    return {
        "deployment": DeploymentResponse.model_validate(
            _build_response(deployment, device_map.get(deployment.id, []))
        ),
        "is_running": is_running,
        "pid": monitor.get_pid(deployment.id),
    }
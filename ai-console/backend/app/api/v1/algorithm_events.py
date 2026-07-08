import json
import os
import logging
import uuid as _uuid
import httpx
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy import select, func, false
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.media import (
    DATA_ROOT as _DATA_ROOT,
    detection_storage_path,
    detection_url,
    normalize_media_url as _normalize_media_url,
    ensure_valid_media_url,
    file_size_for_path,
)
from app.models.warning_event import WarningEvent
from app.models.device import Device
from app.models.event_type import EventType
from app.models.file import File, FileSourceType
from app.models.organization import Organization
from app.models.region import Region
from app.models.algorithm import Algorithm
from app.models.deployment import Deployment
from app.models.deployment_device import DeploymentDevice
from app.models.video_setting import VideoSetting

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/algorithm-events", tags=["algorithm-events"])


async def _fetch_and_save_media(url: str, save_path: Path) -> bool:
    """从 traffic-api 拉取媒体文件 → 写到 save_path。

    traffic-api 写文件到 /mnt/home/api/traffic/api_service/uploads/...,
    ingest 时 ai-console 主动拉取 (traffic-api 零改动)。

    Returns True if saved, False on any error (logged warning).
    """
    try:
        # 相对路径 "/uploads/..." → 拼 traffic-api base_url
        if url.startswith("/"):
            base = settings.TRAFFIC_API_BASE_URL.rstrip("/")
            full_url = f"{base}{url}"
        else:
            full_url = url

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(full_url)
            resp.raise_for_status()
            save_path.parent.mkdir(parents=True, exist_ok=True)
            save_path.write_bytes(resp.content)
            return True
    except Exception as e:
        logger.warning(f"_fetch_and_save_media 失败 ({url}): {e}")
        return False


# Maps traffic payload keys to event_type.name values.
_EVENT_KEY_TO_TYPE = {
    "jam": "jam",
    "anomaly": "anomaly",
    "flow": "flow",
    "reverse": "reverse",
    "pedestrian": "pedestrian",
    "accident": "accident",
    "vest": "vest",
}


async def _resolve_region_ids(db: AsyncSession, region_name: Optional[str]) -> Optional[list[int]]:
    """Resolve region name to a list of region IDs including children.
    Returns None if no region_name provided, empty list if region not found.
    """
    if not region_name:
        return None
    result = await db.execute(
        select(Region).where(Region.name == region_name, Region.deleted_at.is_(None))
    )
    region = result.scalar_one_or_none()
    if not region:
        return []
    region_ids = [region.id]
    children_result = await db.execute(
        select(Region).where(Region.parent_id == region.id, Region.deleted_at.is_(None))
    )
    region_ids.extend([c.id for c in children_result.scalars().all()])
    return region_ids


@router.get("", response_model=dict)
async def list_algorithm_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    companyName: Optional[str] = Query(None),
    regionName: Optional[str] = Query(None),
    algorithmName: Optional[str] = Query(None),
    eventType: Optional[str] = Query(None),
    deviceName: Optional[str] = Query(None),
    isCompliant: Optional[str] = Query(None),
    processStatus: Optional[str] = Query(None),
    startTime: Optional[str] = Query(None),
    endTime: Optional[str] = Query(None),
    deviceId: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated algorithm events in frontend-compatible format."""
    region_ids = await _resolve_region_ids(db, regionName)

    query = (
        select(
            WarningEvent,
            Device.name.label("device_name"),
            EventType.name.label("event_type_name"),
            Organization.name.label("org_name"),
            Region.name.label("region_name"),
            Algorithm.name.label("algorithm_name"),
        )
        .outerjoin(Device, WarningEvent.device_id == Device.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .outerjoin(Organization, WarningEvent.org_id == Organization.id)
        .outerjoin(Region, WarningEvent.region_id == Region.id)
        .outerjoin(Algorithm, WarningEvent.algorithm_id == Algorithm.id)
        .where(WarningEvent.deleted_at.is_(None))
        .order_by(WarningEvent.created_at.desc())
    )

    if deviceId is not None:
        query = query.where(WarningEvent.device_id == deviceId)

    if companyName:
        query = query.where(Organization.name == companyName)
    if region_ids is not None:
        if region_ids:
            query = query.where(WarningEvent.region_id.in_(region_ids))
        else:
            query = query.where(false())
    if algorithmName:
        query = query.where(Algorithm.name == algorithmName)
    if eventType:
        query = query.where(EventType.name.ilike(f"%{eventType}%"))
    if deviceName:
        query = query.where(Device.name.ilike(f"%{deviceName}%"))
    if isCompliant:
        query = query.where(WarningEvent.is_compliant == (isCompliant == "是"))
    if processStatus:
        query = query.where(WarningEvent.process_status == processStatus)
    if startTime:
        try:
            start_dt = datetime.fromisoformat(startTime.replace("Z", "+00:00"))
            query = query.where(WarningEvent.report_time >= start_dt)
        except ValueError:
            pass
    if endTime:
        try:
            end_dt = datetime.fromisoformat(endTime.replace("Z", "+00:00"))
            query = query.where(WarningEvent.report_time <= end_dt)
        except ValueError:
            pass

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for event, device_name, event_type_name, org_name, region_name, algorithm_name in rows:
        items.append({
            "id": event.id,
            "companyName": org_name or "未知公司",
            "regionName": region_name or "未知区域",
            "deviceName": device_name or f"设备-{event.device_id or '未知'}",
            "algorithmName": algorithm_name or "未知算法",
            "eventTypeName": event_type_name or "未知事件",
            "eventDetail": event.event_detail or "",
            "processStatus": event.process_status or "未处置",
            "reportTime": (
                event.report_time.isoformat()
                if event.report_time
                else event.created_at.isoformat()
            ),
            "isCompliant": "是" if event.is_compliant is True else ("否" if event.is_compliant is False else "未知"),
            "is_compliant": event.is_compliant if isinstance(event.is_compliant, bool) else None,
            "imageUrl": ensure_valid_media_url(event.image_url) or "",
            "videoUrl": ensure_valid_media_url(event.video_url) or "",
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/export")
async def export_algorithm_events(
    companyName: Optional[str] = Query(None),
    regionName: Optional[str] = Query(None),
    algorithmName: Optional[str] = Query(None),
    eventType: Optional[str] = Query(None),
    deviceName: Optional[str] = Query(None),
    isCompliant: Optional[str] = Query(None),
    processStatus: Optional[str] = Query(None),
    startTime: Optional[str] = Query(None),
    endTime: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Export algorithm events as CSV/Excel (placeholder)."""
    from fastapi.responses import StreamingResponse
    import io
    import csv

    region_ids = await _resolve_region_ids(db, regionName)

    query = (
        select(
            WarningEvent,
            Device.name.label("device_name"),
            EventType.name.label("event_type_name"),
            Organization.name.label("org_name"),
            Region.name.label("region_name"),
            Algorithm.name.label("algorithm_name"),
        )
        .outerjoin(Device, WarningEvent.device_id == Device.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .outerjoin(Organization, WarningEvent.org_id == Organization.id)
        .outerjoin(Region, WarningEvent.region_id == Region.id)
        .outerjoin(Algorithm, WarningEvent.algorithm_id == Algorithm.id)
        .where(WarningEvent.deleted_at.is_(None))
        .order_by(WarningEvent.created_at.desc())
    )

    if companyName:
        query = query.where(Organization.name == companyName)
    if region_ids is not None:
        if region_ids:
            query = query.where(WarningEvent.region_id.in_(region_ids))
        else:
            query = query.where(false())
    if algorithmName:
        query = query.where(Algorithm.name == algorithmName)
    if eventType:
        query = query.where(EventType.name.ilike(f"%{eventType}%"))
    if deviceName:
        query = query.where(Device.name.ilike(f"%{deviceName}%"))
    if isCompliant:
        query = query.where(WarningEvent.is_compliant == (isCompliant == "是"))
    if processStatus:
        query = query.where(WarningEvent.process_status == processStatus)

    result = await db.execute(query)
    rows = result.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Company", "Region", "Device", "Algorithm", "Event Type", "Detail", "Status", "Report Time", "Is Compliant"])

    for event, device_name, event_type_name, org_name, region_name, algorithm_name in rows:
        writer.writerow([
            event.id,
            org_name or "",
            region_name or "",
            device_name or "",
            algorithm_name or "",
            event_type_name or "",
            event.event_detail or "",
            event.process_status or "",
            event.report_time.isoformat() if event.report_time else "",
            "是" if event.is_compliant else "否",
        ])

    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=algorithm_events.csv"},
    )


@router.post("/{item_id}/handle")
async def handle_algorithm_event(
    item_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
):
    """Handle (dispose) an algorithm event."""
    result = await db.execute(
        select(WarningEvent).where(
            WarningEvent.id == item_id,
            WarningEvent.deleted_at.is_(None),
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    event.process_status = "resolved"
    await db.commit()
    await db.refresh(event)
    return {"id": event.id, "status": event.process_status}


def _parse_report_time(raw: Any) -> Optional[datetime]:
    if raw is None:
        return None
    if isinstance(raw, (int, float)):
        return datetime.fromtimestamp(raw, tz=timezone.utc)
    if isinstance(raw, str):
        s = raw.replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(s)
        except ValueError:
            try:
                return datetime.fromtimestamp(float(s), tz=timezone.utc)
            except ValueError:
                return None
    return None


async def _get_deployment_by_token(db: AsyncSession, token: str) -> Deployment:
    """保留签名以便兼容旧调用点；实际鉴权已改为 TRAFFIC_API_AUTH_TOKEN（见 ingest_algorithm_event）。"""
    result = await db.execute(
        select(Deployment).where(
            Deployment.deployment_token == token,
            Deployment.deleted_at.is_(None),
        )
    )
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid deployment token",
        )
    return deployment


async def _find_active_deployment_for_device(db: AsyncSession, device_id: int) -> Optional[Deployment]:
    """根据 device_id 反查 active deployment（algorithm_status in {running, pending, stopping, completed}）。"""
    result = await db.execute(
        select(Deployment)
        .join(DeploymentDevice, DeploymentDevice.deployment_id == Deployment.id)
        .where(
            DeploymentDevice.device_id == device_id,
            Deployment.deleted_at.is_(None),
            Deployment.algorithm_status.in_(("running", "pending", "stopping", "completed")),
        )
        .order_by(Deployment.id.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


class _EmptyDeploymentContext:
    """无 active deployment 时的占位上下文（不写 org/region/algorithm 字段）。"""
    id = None
    org_id = None
    region_id = None
    algorithm_id = None
    algorithm_status = "unknown"


def _empty_deployment_context() -> _EmptyDeploymentContext:
    return _EmptyDeploymentContext()


async def _verify_traffic_api_token(authorization: Optional[str], db: AsyncSession) -> None:
    """鉴权 traffic-api 推送：接受任一种 token。

    1. 全局 token `settings.TRAFFIC_API_AUTH_TOKEN`（管理面鉴权）
    2. 任一 active deployment 的 `deployment.deployment_token`（traffic-api 子进程推 callback 用的 `cbk_` token）

    traffic-api /start 时为每个 deployment 生成独立的 `cbk_<random>` token（见
    deployment_service.py:41-43 / api_service:195-198）并通过 `result["callback_token"]` 返回,
    ai-console 在 deployments.py:608-614 写入 deployment.deployment_token。traffic-api
    子进程随后用这个 `cbk_` token 推 callback — 所以 ingest 必须接受它,不能只看全局 token。
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization[len("Bearer "):].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token",
        )
    # 1) 全局 token
    expected = settings.TRAFFIC_API_AUTH_TOKEN
    if expected and token == expected:
        return
    # 2) 任一 active deployment 的 callback token
    result = await db.execute(
        select(Deployment.deployment_token).where(
            Deployment.deployment_token == token,
            Deployment.deleted_at.is_(None),
        )
    )
    if result.scalar_one_or_none() is not None:
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid traffic-api token",
    )


async def _resolve_device_id(
    db: AsyncSession,
    deployment: Deployment,
    stream_id: str,
) -> int:
    config = deployment.config_json or {}
    stream_map = config.get("stream_map") or {}
    for device_id_raw, mapped_stream in stream_map.items():
        if str(mapped_stream) == str(stream_id):
            return int(device_id_raw)

    result = await db.execute(
        select(DeploymentDevice.device_id).where(
            DeploymentDevice.deployment_id == deployment.id
        )
    )
    device_ids = [row[0] for row in result.all()]
    if len(device_ids) == 1:
        return device_ids[0]

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"Could not resolve device_id for stream_id {stream_id}",
    )


async def _load_traffic_event_types(db: AsyncSession) -> dict[str, int]:
    result = await db.execute(
        select(EventType.name, EventType.id)
        .join(Algorithm, EventType.algorithm_id == Algorithm.id)
        .where(Algorithm.name == "traffic", EventType.deleted_at.is_(None))
    )
    return {name: id for name, id in result.all()}


async def _get_allowed_event_type_ids(
    db: AsyncSession,
    device_id: int,
) -> Optional[set[int]]:
    """Return the set of event_type IDs enabled in the VideoSetting for this device.

    Returns None if no VideoSetting manages this device (backward compatibility:
    accept all events). Returns an empty set if the setting is disabled.
    """
    result = await db.execute(
        select(VideoSetting).where(
            VideoSetting.device_ids.contains([device_id]),
            VideoSetting.deleted_at.is_(None),
        )
    )
    setting = result.scalars().first()
    if setting is None:
        return None
    if not setting.status:
        return set()
    return set(setting.event_types or [])


async def _create_file_for_event(
    db: AsyncSession,
    warning_event: WarningEvent,
    url: Optional[str],
    source_type: FileSourceType,
    device_id: Optional[int],
    event_name: str,
    device_name: str,
    timestamp: str,
    salt: str,
    tmp_pairs: list[tuple[Path, Path]],
) -> None:
    """两阶段写：先写 .tmp，DB 入库仍指向 final，tmp_pairs 留给 caller commit 后 rename。

    Args:
        event_name: e.g. "pedestrian" (from event_type.name)
        device_name: e.g. "北区-设备1" (from device.name)
        timestamp: e.g. "20260701123045" (from report_time)
        salt: 每 ingest batch 唯一 (uuid4 hex), 防并发同秒冲突
        tmp_pairs: 调用方传入的空 list；写盘成功后追加 (tmp_path, save_path)，
                   供 caller 在 db.commit() 成功后原子 rename。
    """
    if not url:
        return

    file_kind = "image" if source_type == FileSourceType.WARNING_EVENT_IMAGE else "video"
    ext = "jpg" if file_kind == "image" else "mp4"
    save_path = detection_storage_path(event_name, device_name, timestamp, salt, file_kind)
    new_url = detection_url(event_name, device_name, timestamp, salt, file_kind)

    # [两阶段] 先写 .tmp；DB commit 成功后才由 caller rename 到 final。
    # 这样 commit 失败时不需要回滚磁盘（.tmp 已被 caller 删掉），无孤儿文件。
    tmp_path = save_path.with_suffix(save_path.suffix + ".tmp")
    success = await _fetch_and_save_media(url, tmp_path)
    if not success or not tmp_path.exists():
        return  # 失败不入库，tmp 也不留

    file_size = tmp_path.stat().st_size

    file_record = File(
        warning_event_id=warning_event.id,
        source_type=source_type.value,
        file_name=f"{file_kind}.{ext}",
        file_type=file_kind,  # "image" or "video"（与 model 字段类型一致）
        storage_path=str(save_path),  # 指向最终路径（DB 提交后才存在）
        url=new_url,
        file_size_bytes=file_size,
        device_id=device_id,
    )
    db.add(file_record)

    # [方案 C] ingest 落地成功后,把 warning_event.image_url / video_url 同步覆盖成本地 URL。
    # 原始来源 URL 用完即丢(来源服务可能挂),所有读取方都拿本地可显示的 /data/... 路径。
    # 只在当前字段还是"原始 URL"(非空且非 /data/ 前缀)时覆盖,避免无谓写。
    if file_kind == "image":
        if warning_event.image_url and not warning_event.image_url.startswith("/data/"):
            warning_event.image_url = new_url
    elif file_kind == "video":
        if warning_event.video_url and not warning_event.video_url.startswith("/data/"):
            warning_event.video_url = new_url

    tmp_pairs.append((tmp_path, save_path))


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_algorithm_event(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    authorization: Optional[str] = Header(None),
):
    """traffic-api 子进程 / 用户后端推送的事件入库。

    鉴权：Authorization: Bearer <TRAFFIC_API_AUTH_TOKEN>。
    不再校验 deployment_token（traffic-api / 用户后端用设备面 token 推）。
    device_id 由 stream_id（==str(device_id)）解析，强约束（API_SERVICE(1).md L130-133）。
    """
    await _verify_traffic_api_token(authorization, db)

    stream_id = payload.get("stream_id")
    if not stream_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="stream_id is required",
        )

    # stream_id == str(device_id) 强约束：直接转 int 作为 device_id。
    try:
        device_id = int(stream_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="stream_id must equal str(device_id)",
        )

    # 找该 device 上的 active deployment（用于继承 org_id/region_id/algorithm_id）。
    deployment = await _find_active_deployment_for_device(db, device_id)
    if deployment is None:
        # traffic-api 推送时 deployment 状态为 'running' 即可接受；
        # 找不到 active deployment 时仍允许入库（用户后端可能同步历史事件）。
        deployment = _empty_deployment_context()
    event_type_map = await _load_traffic_event_types(db)
    allowed_event_type_ids = await _get_allowed_event_type_ids(db, device_id)
    report_time = _parse_report_time(payload.get("timestamp"))

    # Modules may send either *_url or *_path; normalize to /data/... URLs.
    image_url = _normalize_media_url(payload.get("image_url") or payload.get("image_path"))
    video_url = _normalize_media_url(payload.get("video_url") or payload.get("video_path"))

    # Traffic modules push a stat payload every frame regardless of whether
    # anything was detected, and only attach image_url/video_url when a real
    # event snapshot/clip was saved. Skip payloads that carry no media so we
    # don't pollute the event list with empty stat rows.
    if not image_url and not video_url:
        return {"message": "no media, skipped", "event_ids": []}

    # [NEW] auto-detection-folder: 查 device.name + 生成 batch salt + timestamp
    device = await db.get(Device, device_id)
    device_name = device.name if device else f"dev_{device_id}"
    salt = _uuid.uuid4().hex
    timestamp = report_time.strftime("%Y%m%d%H%M%S")

    created_events: list[WarningEvent] = []
    for key, event_data in payload.items():
        if key not in _EVENT_KEY_TO_TYPE or not event_data:
            continue
        event_type_name = _EVENT_KEY_TO_TYPE[key]
        event_type_id = event_type_map.get(event_type_name)
        if not event_type_id:
            continue
        if allowed_event_type_ids is not None and event_type_id not in allowed_event_type_ids:
            # Event type is not enabled in the VideoSetting for this device.
            continue

        event = WarningEvent(
            device_id=device_id,
            org_id=deployment.org_id,
            region_id=deployment.region_id,
            algorithm_id=deployment.algorithm_id,
            event_type_id=event_type_id,
            event_detail=json.dumps(event_data, ensure_ascii=False)[:1000],
            report_time=report_time,
            process_status="pending",
            image_url=image_url,
            video_url=video_url,
        )
        # Attach the originating payload key (e.g. "jam", "flow") so the
        # post-commit WS broadcast can use it as event_type_name without a
        # second round-trip to the DB to resolve event_type_id.
        event._payload_key = key  # type: ignore[attr-defined]
        db.add(event)
        created_events.append(event)

    if not created_events:
        return {"message": "no events ingested", "event_ids": []}

    await db.flush()

    # Explicitly create File records for every event with media URLs.
    # [NEW] 传 event_name (来自 _EVENT_KEY_TO_TYPE) + device_name + timestamp + salt
    # 生成 data/photo-videos/{event}/{event}_{device}_{ts}_{uuid8}/image.jpg|video.mp4
    # [两阶段] tmp_pairs 收集 (tmp_path, save_path)；commit 成功后才 rename 到 final。
    tmp_pairs: list[tuple[Path, Path]] = []
    for event in created_events:
        event_name = event._payload_key  # e.g. "pedestrian", "accident"
        await _create_file_for_event(
            db, event, image_url, FileSourceType.WARNING_EVENT_IMAGE,
            device_id, event_name=event_name, device_name=device_name,
            timestamp=timestamp, salt=salt, tmp_pairs=tmp_pairs,
        )
        await _create_file_for_event(
            db, event, video_url, FileSourceType.WARNING_EVENT_VIDEO,
            device_id, event_name=event_name, device_name=device_name,
            timestamp=timestamp, salt=salt, tmp_pairs=tmp_pairs,
        )

    # [两阶段] DB commit + 磁盘 rename 生命周期：
    #   - commit 失败 → 清掉所有 .tmp + rollback + raise（无孤儿文件）
    #   - commit 成功 → 原子 rename .tmp → final（POSIX rename 同分区原子）
    try:
        await db.commit()
    except Exception as commit_err:
        for tmp_path, _ in tmp_pairs:
            tmp_path.unlink(missing_ok=True)
        await db.rollback()
        logger.error(
            f"ingest commit 失败，已清理 {len(tmp_pairs)} 个 .tmp 文件: {commit_err}"
        )
        raise

    # rename 在 commit 之后；单条失败不影响其他 rename
    for tmp_path, final_path in tmp_pairs:
        try:
            os.rename(tmp_path, final_path)
        except OSError as rename_err:
            logger.error(
                f"rename 失败 {tmp_path.name} → {final_path.name}: {rename_err} "
                f"(DB 已提交，需要 cleanup 工具扫 .tmp)"
            )

    for event in created_events:
        await db.refresh(event)

    # Broadcast to WebSocket subscribers (MonitorWall / MonitorSingle).
    # Imported lazily to avoid circular import at module load time.
    # Wrapped in try/except so a broadcast failure never breaks the main
    # ingest flow — the event is already persisted, the push is best-effort.
    try:
        from app.api.v1.ws_realtime import manager as _ws_manager

        for event in created_events:
            try:
                event_detail_dict = (
                    json.loads(event.event_detail) if event.event_detail else None
                )
            except (TypeError, ValueError):
                event_detail_dict = None

            try:
                await _ws_manager.broadcast_event(
                    device_id,
                    {
                        "type": "event",
                        "id": event.id,
                        "event_type": getattr(event, "_payload_key", None),
                        "image_url": event.image_url,
                        "video_url": event.video_url,
                        "report_time": event.report_time.isoformat() if event.report_time else None,
                        "event_detail": event_detail_dict,
                    },
                )
            except Exception as broadcast_err:  # noqa: BLE001
                logger.warning("WS broadcast failed for event %s: %s", event.id, broadcast_err)
    except Exception as outer_err:  # noqa: BLE001
        # ws_realtime import failed (e.g. circular import) — log and continue.
        logger.warning("WS realtime unavailable, continuing without push: %s", outer_err)

    return {"event_ids": [event.id for event in created_events]}

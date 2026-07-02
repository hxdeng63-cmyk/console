from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.core.database import get_db
from app.core.media import ensure_valid_media_url
from app.models.warning_event import WarningEvent
from app.models.device import Device
from app.models.event_type import EventType
from app.models.organization import Organization
from app.models.region import Region

router = APIRouter(prefix="/warning-events", tags=["warning-events"])


def _resolve_location(
    event_detail: Optional[str],
    device_name: Optional[str],
    org_name: Optional[str] = None,
    big_region_name: Optional[str] = None,
    small_region_name: Optional[str] = None,
) -> str:
    """Resolve human-readable location with a clear fallback chain.

    Priority:
      1. Full 4-level path: "{org} {bigRegion}-{smallRegion}-{deviceName}"
         (only when org/region/device are all resolvable)
      2. 3-level path without org: "{bigRegion}-{smallRegion}-{deviceName}"
      3. Device.name — acts as the device's human-readable label when region
         info is missing.
      4. event_detail — only as a last resort, and only if it looks like
         prose. JSON blobs are truncated to 50 chars to avoid leaking
         `{"up_count": 10, ...}` into the UI.
    """
    # 1) Full 4-level path.
    if org_name and big_region_name and small_region_name and device_name:
        return f"{org_name} {big_region_name}-{small_region_name}-{device_name}"
    # 2) 3-level path without org.
    if big_region_name and small_region_name and device_name:
        return f"{big_region_name}-{small_region_name}-{device_name}"
    # 3) Device-level identifier (name used as location proxy).
    if device_name:
        return device_name

    # 4) Last-resort: event_detail.
    if event_detail:
        stripped = event_detail.strip()
        looks_like_json = stripped.startswith("{") or stripped.startswith("[")
        if looks_like_json:
            return f"{event_detail[:50]}…" if len(event_detail) > 50 else event_detail
        return event_detail

    return "未知位置"


class WarningEventItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cameraName: Optional[str] = None
    eventType: Optional[str] = None
    time: Optional[str] = None
    level: str = "low"
    location: Optional[str] = None
    status: str = "pending"
    imageUrl: Optional[str] = None
    deviceId: Optional[int] = None
    eventDetail: Optional[str] = None
    isCompliant: Optional[bool] = None
    videoUrl: Optional[str] = None


@router.get("", response_model=dict)
async def list_warning_events(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    event_type: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    start_time: Optional[datetime] = Query(None),
    end_time: Optional[datetime] = Query(None),
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated warning events list."""
    SmallRegion = aliased(Region, name='small_region')
    BigRegion = aliased(Region, name='big_region')
    query = (
        select(
            WarningEvent,
            Device.name.label("device_name"),
            EventType.name.label("event_type_name"),
            EventType.severity.label("event_severity"),
            Organization.name.label("org_name"),
            SmallRegion.name.label("small_region_name"),
            BigRegion.name.label("big_region_name"),
        )
        .outerjoin(Device, WarningEvent.device_id == Device.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .outerjoin(Organization, Device.org_id == Organization.id)
        .outerjoin(SmallRegion, Device.region_id == SmallRegion.id)
        .outerjoin(BigRegion, SmallRegion.parent_id == BigRegion.id)
        .where(WarningEvent.deleted_at.is_(None))
        .order_by(WarningEvent.created_at.desc())
    )

    if status:
        query = query.where(WarningEvent.process_status == status)
    if event_type:
        # Exact match against EventType.name (e.g. "flow", "jam").
        # Previously used ilike, which caused false positives (e.g. "flow"
        # also matched "overflow" / "traffic_flow"). Frontend callers send
        # canonical short codes that map 1:1 to EventType.name values.
        query = query.where(EventType.name == event_type)
    if keyword:
        query = query.where(
            (Device.name.ilike(f"%{keyword}%"))
            | (WarningEvent.event_detail.ilike(f"%{keyword}%"))
        )
    if start_time:
        query = query.where(WarningEvent.report_time >= start_time)
    if end_time:
        query = query.where(WarningEvent.report_time <= end_time)
    if device_id:
        query = query.where(WarningEvent.device_id == device_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    severity_to_level = {1: "low", 2: "medium", 3: "high", 4: "critical"}

    items = []
    for event, device_name, event_type_name, event_severity, org_name, small_region_name, big_region_name in rows:
        level = severity_to_level.get(event_severity or 1, "low")
        items.append({
            "id": event.id,
            "cameraName": device_name or f"摄像头-{event.device_id or '未知'}",
            "eventType": event_type_name or "未知事件",
            "time": (
                event.report_time.isoformat()
                if event.report_time
                else event.created_at.isoformat()
            ),
            "level": level,
            "location": _resolve_location(
                event.event_detail, device_name, org_name, big_region_name, small_region_name,
            ),
            "status": event.process_status,
            "imageUrl": ensure_valid_media_url(event.image_url),
            "deviceId": event.device_id,
            "eventDetail": event.event_detail,
            "isCompliant": event.is_compliant,
            "videoUrl": ensure_valid_media_url(event.video_url),
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=WarningEventItem)
async def get_warning_event(item_id: int, db: AsyncSession = Depends(get_db)):
    """Get a single warning event by ID."""
    SmallRegion = aliased(Region, name='small_region')
    BigRegion = aliased(Region, name='big_region')
    result = await db.execute(
        select(
            WarningEvent,
            Device.name.label("device_name"),
            EventType.name.label("event_type_name"),
            EventType.severity.label("event_severity"),
            Organization.name.label("org_name"),
            SmallRegion.name.label("small_region_name"),
            BigRegion.name.label("big_region_name"),
        )
        .outerjoin(Device, WarningEvent.device_id == Device.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .outerjoin(Organization, Device.org_id == Organization.id)
        .outerjoin(SmallRegion, Device.region_id == SmallRegion.id)
        .outerjoin(BigRegion, SmallRegion.parent_id == BigRegion.id)
        .where(WarningEvent.id == item_id, WarningEvent.deleted_at.is_(None))
    )
    row = result.one_or_none()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Warning event not found")

    event, device_name, event_type_name, event_severity, org_name, small_region_name, big_region_name = row
    severity_to_level = {1: "low", 2: "medium", 3: "high", 4: "critical"}
    level = severity_to_level.get(event_severity or 1, "low")

    return WarningEventItem(
        id=event.id,
        cameraName=device_name or f"摄像头-{event.device_id or '未知'}",
        eventType=event_type_name or "未知事件",
        time=(
            event.report_time.isoformat()
            if event.report_time
            else event.created_at.isoformat()
        ),
        level=level,
        location=_resolve_location(
            event.event_detail, device_name, org_name, big_region_name, small_region_name,
        ),
        status=event.process_status,
        imageUrl=ensure_valid_media_url(event.image_url),
        deviceId=event.device_id,
        eventDetail=event.event_detail,
        isCompliant=event.is_compliant,
        videoUrl=ensure_valid_media_url(event.video_url),
    )


@router.put("/{item_id}/status")
async def update_warning_event_status(
    item_id: int,
    status: str = Query(..., regex="^(pending|processing|resolved|ignored)$"),
    db: AsyncSession = Depends(get_db),
):
    """Update the process status of a warning event."""
    result = await db.execute(
        select(WarningEvent).where(
            WarningEvent.id == item_id, WarningEvent.deleted_at.is_(None)
        )
    )
    event = result.scalar_one_or_none()
    if not event:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Warning event not found")

    event.process_status = status
    await db.commit()
    await db.refresh(event)
    return {"id": event.id, "status": event.process_status}

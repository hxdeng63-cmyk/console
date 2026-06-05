from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.warning_event import WarningEvent
from app.models.device import Device
from app.models.event_type import EventType

router = APIRouter(prefix="/warning-events", tags=["warning-events"])


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
    db: AsyncSession = Depends(get_db),
):
    """Return paginated warning events list."""
    query = (
        select(
            WarningEvent,
            Device.name.label("device_name"),
            EventType.name.label("event_type_name"),
            EventType.severity.label("event_severity"),
        )
        .outerjoin(Device, WarningEvent.device_id == Device.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .where(WarningEvent.deleted_at.is_(None))
        .order_by(WarningEvent.created_at.desc())
    )

    if status:
        query = query.where(WarningEvent.process_status == status)
    if event_type:
        query = query.where(EventType.name.ilike(f"%{event_type}%"))
    if keyword:
        query = query.where(
            (Device.name.ilike(f"%{keyword}%"))
            | (WarningEvent.event_detail.ilike(f"%{keyword}%"))
        )
    if start_time:
        query = query.where(WarningEvent.report_time >= start_time)
    if end_time:
        query = query.where(WarningEvent.report_time <= end_time)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    severity_to_level = {1: "low", 2: "medium", 3: "high", 4: "critical"}

    items = []
    for event, device_name, event_type_name, event_severity in rows:
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
            "location": event.event_detail or "未知位置",
            "status": event.process_status,
            "imageUrl": event.image_url,
            "deviceId": event.device_id,
            "eventDetail": event.event_detail,
            "isCompliant": event.is_compliant,
            "videoUrl": event.video_url,
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
    result = await db.execute(
        select(
            WarningEvent,
            Device.name.label("device_name"),
            EventType.name.label("event_type_name"),
            EventType.severity.label("event_severity"),
        )
        .outerjoin(Device, WarningEvent.device_id == Device.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .where(WarningEvent.id == item_id, WarningEvent.deleted_at.is_(None))
    )
    row = result.one_or_none()
    if not row:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Warning event not found")

    event, device_name, event_type_name, event_severity = row
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
        location=event.event_detail or "未知位置",
        status=event.process_status,
        imageUrl=event.image_url,
        deviceId=event.device_id,
        eventDetail=event.event_detail,
        isCompliant=event.is_compliant,
        videoUrl=event.video_url,
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

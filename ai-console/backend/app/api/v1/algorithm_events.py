from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.warning_event import WarningEvent
from app.models.device import Device
from app.models.event_type import EventType
from app.models.organization import Organization
from app.models.region import Region
from app.models.algorithm import Algorithm

router = APIRouter(prefix="/algorithm-events", tags=["algorithm-events"])


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
    db: AsyncSession = Depends(get_db),
):
    """Return paginated algorithm events in frontend-compatible format."""
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
    if regionName:
        query = query.where(Region.name == regionName)
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
                event.report_time.strftime("%Y-%m-%d %H:%M:%S")
                if event.report_time
                else event.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ),
            "isCompliant": "是" if event.is_compliant is True else ("否" if event.is_compliant is False else "未知"),
            "imageUrl": event.image_url or "",
            "videoUrl": event.video_url or "",
            "detectBox": {"top": "0%", "left": "0%", "width": "0%", "height": "0%"},
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
    if regionName:
        query = query.where(Region.name == regionName)
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
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Event not found")

    event.process_status = "resolved"
    await db.commit()
    await db.refresh(event)
    return {"id": event.id, "status": event.process_status}

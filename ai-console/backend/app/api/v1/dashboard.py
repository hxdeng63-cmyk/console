from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.deployment import Deployment
from app.models.algorithm import Algorithm
from app.models.warning_event import WarningEvent
from app.models.device import Device
from app.models.event_type import EventType

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Return overall dashboard statistics."""
    total_devices_result = await db.execute(
        select(func.count()).select_from(Device).where(Device.deleted_at.is_(None))
    )
    total_devices = total_devices_result.scalar() or 0

    active_devices_result = await db.execute(
        select(func.count()).select_from(Device).where(
            Device.deleted_at.is_(None), Device.status == "active"
        )
    )
    active_devices = active_devices_result.scalar() or 0

    total_events_result = await db.execute(
        select(func.count()).select_from(WarningEvent).where(
            WarningEvent.deleted_at.is_(None)
        )
    )
    total_events = total_events_result.scalar() or 0

    pending_events_result = await db.execute(
        select(func.count()).select_from(WarningEvent).where(
            WarningEvent.deleted_at.is_(None),
            WarningEvent.process_status == "pending",
        )
    )
    pending_events = pending_events_result.scalar() or 0

    avg_speed = 42.5
    up_traffic = 128.6
    down_traffic = 256.3
    road_level = 2
    road_level_text = "畅通"
    congestion_index = 1.2

    return {
        "avgSpeed": avg_speed,
        "upTraffic": up_traffic,
        "downTraffic": down_traffic,
        "roadLevel": road_level,
        "roadLevelText": road_level_text,
        "congestionIndex": congestion_index,
        "totalDevices": total_devices,
        "activeDevices": active_devices,
        "totalEvents": total_events,
        "pendingEvents": pending_events,
    }


@router.get("/event-stats")
async def get_event_stats(db: AsyncSession = Depends(get_db)):
    """Return event statistics grouped by event type."""
    result = await db.execute(
        select(
            EventType.name,
            EventType.severity,
            func.count(WarningEvent.id).label("value"),
        )
        .join(WarningEvent, WarningEvent.event_type_id == EventType.id)
        .where(WarningEvent.deleted_at.is_(None), EventType.deleted_at.is_(None))
        .group_by(EventType.id, EventType.name, EventType.severity)
    )

    rows = result.all()
    color_map = {
        1: "#67C23A",
        2: "#E6A23C",
        3: "#F56C6C",
        4: "#909399",
    }

    legend = []
    total = 0
    for name, severity, value in rows:
        legend.append({
            "name": name,
            "value": value,
            "color": color_map.get(severity, "#409EFF"),
        })
        total += value

    if not legend:
        legend = [
            {"name": "人员聚集", "value": 35, "color": "#F56C6C"},
            {"name": "非法入侵", "value": 28, "color": "#E6A23C"},
            {"name": "车辆违停", "value": 20, "color": "#67C23A"},
            {"name": "烟火检测", "value": 15, "color": "#409EFF"},
            {"name": "其他", "value": 2, "color": "#909399"},
        ]
        total = 100

    return {"total": total, "legend": legend}


@router.get("/deployments")
async def get_dashboard_deployments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Return deployment data list for dashboard."""
    query = (
        select(Deployment, Algorithm.name.label("algorithm_name"))
        .outerjoin(Algorithm, Deployment.algorithm_id == Algorithm.id)
        .where(Deployment.deleted_at.is_(None))
        .order_by(Deployment.created_at.desc())
    )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for deployment, algorithm_name in rows:
        camera_count_result = await db.execute(
            select(func.count()).select_from(Device).where(
                Device.deleted_at.is_(None), Device.status == "active"
            )
        )
        camera_count = camera_count_result.scalar() or 0

        event_count_result = await db.execute(
            select(func.count()).select_from(WarningEvent).where(
                WarningEvent.deleted_at.is_(None),
                WarningEvent.algorithm_id == deployment.algorithm_id,
            )
        )
        event_count = event_count_result.scalar() or 0

        items.append({
            "id": deployment.id,
            "name": deployment.name,
            "status": deployment.status,
            "algorithmStatus": deployment.algorithm_status,
            "cameraCount": camera_count,
            "eventCount": event_count,
            "algorithmName": algorithm_name or "未知算法",
            "deployedAt": deployment.deployed_at.isoformat() if deployment.deployed_at else None,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import WarningEvent

router = APIRouter(prefix="/event-stats", tags=["事件统计"])


@router.get("")
async def get_event_stats(
    dimension: str = Query("day"),
    company: Optional[str] = None,
    region: Optional[str] = None,
    startDate: Optional[str] = None,
    endDate: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(WarningEvent).where(WarningEvent.deleted_at.is_(None))

    # Build trend data based on dimension
    if dimension == "hour":
        times = [f"{h:02d}:00" for h in range(24)]
        values = [0] * 24
    elif dimension == "month":
        times = [f"{i}月" for i in range(1, 13)]
        values = [0] * 12
    else:
        # day - last 7 days
        times = ["03-18", "03-20", "03-22", "03-24", "03-26", "03-28", "03-30"]
        values = [65, 78, 92, 88, 95, 110, 125]

    trend = [{"time": t, "value": v} for t, v in zip(times, values)]

    return {
        "trend": trend,
        "dimension": dimension,
        "company": company,
        "region": region,
    }


@router.get("/scenes")
async def get_scene_stats(db: AsyncSession = Depends(get_db)):
    categories = ["异常停车", "车辆逆行", "车辆超速", "行人闯入", "抛洒物", "拥堵"]
    values = [45, 32, 28, 15, 12, 8]
    today_events = [
        {"name": "异常停车", "value": 12},
        {"name": "车辆逆行", "value": 8},
        {"name": "车辆超速", "value": 6},
        {"name": "行人闯入", "value": 3},
        {"name": "抛洒物", "value": 2},
        {"name": "拥堵", "value": 1},
    ]

    return {
        "categories": categories,
        "values": values,
        "todayEvents": today_events,
    }

from datetime import datetime, timezone, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.warning_event import WarningEvent
from app.models.event_type import EventType
from app.models.algorithm import Algorithm

router = APIRouter(prefix="/event-stats", tags=["事件统计"])

# 业务时区常量：中国大陆业务统一使用 Asia/Shanghai (UTC+8)。
# 所有"今日/昨日"等按自然日划分的统计必须以此为基准，
# 避免 UTC 0 点与中国本地 0 点错位 8 小时导致的统计漏报。
BUSINESS_TZ = timezone(timedelta(hours=8))


def _build_base_query(
    query,
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    device_id: Optional[int] = None,
):
    """共享过滤逻辑。start_date/end_date 为 datetime 对象，确保类型安全。"""
    query = query.where(WarningEvent.deleted_at.is_(None))

    if device_id:
        query = query.where(WarningEvent.device_id == device_id)

    # report_time 为 NULL 的记录用 created_at 兜底
    if org_id:
        query = query.where(WarningEvent.org_id == org_id)
    if region_ids:
        query = query.where(WarningEvent.region_id.in_(region_ids))
    if start_date:
        query = query.where(
            func.coalesce(WarningEvent.report_time, WarningEvent.created_at) >= start_date
        )
    if end_date:
        query = query.where(
            func.coalesce(WarningEvent.report_time, WarningEvent.created_at) <= end_date
        )

    return query


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """将 ISO 格式日期字符串解析为 UTC datetime，无效输入抛 400。"""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, TypeError):
        raise HTTPException(status_code=400, detail=f"Invalid date format: {date_str}")


def _get_today_start() -> datetime:
    """返回今日开始时间（Asia/Shanghai 0 点的 UTC 等价值）。

    在 +8 时区，本地 00:00 = UTC 16:00（前一日）；若仍用 UTC 0 点作为
    "今日起点"，本地 00:00-08:00 这 8 小时的事件会被错误归入"昨日"。
    返回带 tzinfo 的 datetime，与 _build_base_query 中的 datetime 比较保持一致。
    """
    local_now = datetime.now(BUSINESS_TZ)
    local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    return local_midnight.astimezone(timezone.utc)


@router.get("/today")
async def get_today_stats(
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = Query(None),
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    today_start = _get_today_start()

    query = select(
        EventType.name,
        func.count(WarningEvent.id)
    ).select_from(WarningEvent).join(WarningEvent.event_type)
    query = _build_base_query(query, org_id=org_id, region_ids=region_ids, start_date=today_start, device_id=device_id)
    query = query.group_by(EventType.name)

    result = await db.execute(query)
    items = [{"name": name, "value": count} for name, count in result.all()]
    total = sum(item["value"] for item in items)

    return {"items": items, "total": total}


@router.get("/violations")
async def get_violation_stats(
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = Query(None),
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    today_start = _get_today_start()

    query = select(
        EventType.name,
        func.count(WarningEvent.id)
    ).select_from(WarningEvent).join(WarningEvent.event_type).where(
        WarningEvent.is_compliant == False
    )
    query = _build_base_query(query, org_id=org_id, region_ids=region_ids, start_date=today_start, device_id=device_id)
    query = query.group_by(EventType.name)

    result = await db.execute(query)
    items = [{"name": name, "value": count} for name, count in result.all()]

    return {"items": items}


@router.get("/algorithm-summary")
async def get_algorithm_summary(
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(func.count(WarningEvent.id))
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    query = _build_base_query(query, org_id=org_id, region_ids=region_ids, start_date=start_dt, end_date=end_dt, device_id=device_id)

    result = await db.execute(query)
    total = result.scalar() or 0

    return {"total": total, "max": total}


@router.get("/scenes")
async def get_scene_stats(
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    query = select(
        EventType.id,
        EventType.name,
        func.count(WarningEvent.id)
    ).select_from(WarningEvent).join(WarningEvent.event_type)
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    query = _build_base_query(query, org_id=org_id, region_ids=region_ids, start_date=start_dt, end_date=end_dt, device_id=device_id)
    query = query.group_by(EventType.id, EventType.name)

    result = await db.execute(query)
    items = [{"id": et_id, "name": name, "value": count} for et_id, name, count in result.all()]

    return {
        "items": items,
        "categories": [i["name"] for i in items],
        "values": [i["value"] for i in items]
    }


def _get_time_trunc(dimension: str):
    coalesce_time = func.coalesce(WarningEvent.report_time, WarningEvent.created_at)
    return {
        "hour": func.date_trunc("hour", coalesce_time),
        "day": func.date_trunc("day", coalesce_time),
        "month": func.date_trunc("month", coalesce_time),
    }[dimension]


def _format_time_bucket(time_bucket, dimension: str) -> str:
    if dimension == "day":
        return time_bucket.strftime("%m-%d")
    if dimension == "hour":
        return time_bucket.strftime("%H:%M")
    return time_bucket.strftime("%Y-%m")


@router.get("/trend")
async def get_trend_stats(
    dimension: str = Query("day", enum=["hour", "day", "month"]),
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    time_trunc = _get_time_trunc(dimension)

    query = select(
        time_trunc.label("time_bucket"),
        Algorithm.name,
        func.count(WarningEvent.id)
    ).select_from(WarningEvent).join(WarningEvent.algorithm)
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    query = _build_base_query(query, org_id=org_id, region_ids=region_ids, start_date=start_dt, end_date=end_dt, device_id=device_id)
    query = query.group_by("time_bucket", Algorithm.name).order_by("time_bucket")

    result = await db.execute(query)
    rows = result.all()

    data_by_algo = {}
    for time_bucket, algo_name, count in rows:
        time_str = _format_time_bucket(time_bucket, dimension)
        data_by_algo.setdefault(algo_name, []).append({"time": time_str, "value": count})

    merged = {}
    for algo_data in data_by_algo.values():
        for point in algo_data:
            merged[point["time"]] = merged.get(point["time"], 0) + point["value"]

    trend = [{"time": t, "value": v} for t, v in sorted(merged.items())]

    return {"trend": trend, "dimension": dimension}


@router.get("/event-trend")
async def get_event_trend_stats(
    dimension: str = Query("day", enum=["hour", "day", "month"]),
    event_type_id: Optional[int] = None,
    org_id: Optional[int] = None,
    region_ids: Optional[list[int]] = Query(None),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    device_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    time_trunc = _get_time_trunc(dimension)

    query = select(
        time_trunc.label("time_bucket"),
        func.count(WarningEvent.id)
    )
    start_dt = _parse_date(start_date)
    end_dt = _parse_date(end_date)
    query = _build_base_query(query, org_id=org_id, region_ids=region_ids, start_date=start_dt, end_date=end_dt, device_id=device_id)

    if event_type_id:
        query = query.where(WarningEvent.event_type_id == event_type_id)

    query = query.group_by("time_bucket").order_by("time_bucket")

    result = await db.execute(query)
    rows = result.all()

    trend = [{"time": _format_time_bucket(time_bucket, dimension), "value": count} for time_bucket, count in rows]

    return {"trend": trend, "dimension": dimension}

from datetime import datetime
from typing import Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import PushHistory
from app.schemas import PaginatedResponse

router = APIRouter(prefix="/push-histories", tags=["推送历史管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


def serialize_push_history(item) -> dict:
    """Serialize PushHistory model to dict, handling special types"""
    return {
        "id": item.id,
        "rule_id": item.rule_id,
        "device_id": item.device_id,
        "event_type_id": item.event_type_id,
        "push_channels": item.push_channels,
        "push_target": item.push_target,
        "push_time": item.push_time.isoformat() if item.push_time else None,
        "status": item.status,
        "retry_count": item.retry_count,
        "operator": item.operator,
        "count": item.count,
        "detail": item.detail,
        "created_at": item.created_at.isoformat() if item.created_at else None
    }


@router.get("", response_model=PaginatedResponse)
async def list_push_histories(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    rule_id: Optional[int] = None,
    device_id: Optional[int] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取推送历史列表
    - rule_id: 联动规则ID筛选
    - device_id: 设备ID筛选
    - status: 推送状态筛选
    """
    query = select(PushHistory)
    query = soft_delete_query(query, PushHistory)

    if rule_id is not None:
        query = query.where(PushHistory.rule_id == rule_id)

    if device_id is not None:
        query = query.where(PushHistory.device_id == device_id)

    if status:
        query = query.where(PushHistory.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(PushHistory.push_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[serialize_push_history(item) for item in items]
    )


@router.get("/{push_id}", response_model=dict)
async def get_push_history(push_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PushHistory).where(
        PushHistory.id == push_id,
        PushHistory.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="推送记录不存在")
    return serialize_push_history(item)
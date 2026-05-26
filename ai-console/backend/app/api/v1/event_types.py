from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import EventType
from app.schemas import (
    EventTypeCreate, EventTypeUpdate, EventTypeResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/event-types", tags=["事件类型管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_event_types(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    algorithm_id: Optional[int] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(EventType)
    query = soft_delete_query(query, EventType)

    if keyword:
        query = query.where(
            or_(
                EventType.name.ilike(f"%{keyword}%"),
                EventType.description.ilike(f"%{keyword}%")
            )
        )

    if algorithm_id is not None:
        query = query.where(EventType.algorithm_id == algorithm_id)

    if category:
        query = query.where(EventType.category == category)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[EventTypeResponse.model_validate(item) for item in items]
    )


@router.get("/{event_type_id}", response_model=EventTypeResponse)
async def get_event_type(event_type_id: int, db: AsyncSession = Depends(get_db)):
    query = select(EventType).where(
        EventType.id == event_type_id,
        EventType.deleted_at.is_(None)
    )
    result = await db.execute(query)
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="事件类型不存在")
    return event_type


@router.post("", response_model=EventTypeResponse)
async def create_event_type(data: EventTypeCreate, db: AsyncSession = Depends(get_db)):
    event_type = EventType(**data.model_dump())
    db.add(event_type)
    await db.commit()
    await db.refresh(event_type)
    return event_type


@router.put("/{event_type_id}", response_model=EventTypeResponse)
async def update_event_type(
    event_type_id: int,
    data: EventTypeUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(EventType).where(
        EventType.id == event_type_id,
        EventType.deleted_at.is_(None)
    )
    result = await db.execute(query)
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="事件类型不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(event_type, key, value)

    await db.commit()
    await db.refresh(event_type)
    return event_type


@router.delete("/{event_type_id}")
async def delete_event_type(event_type_id: int, db: AsyncSession = Depends(get_db)):
    query = select(EventType).where(
        EventType.id == event_type_id,
        EventType.deleted_at.is_(None)
    )
    result = await db.execute(query)
    event_type = result.scalar_one_or_none()
    if not event_type:
        raise HTTPException(status_code=404, detail="事件类型不存在")

    event_type.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}
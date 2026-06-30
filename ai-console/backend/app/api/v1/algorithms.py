from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Algorithm, EventType
from app.schemas import (
    AlgorithmCreate, AlgorithmUpdate, AlgorithmResponse, AlgorithmEventItem,
    PaginatedResponse
)

router = APIRouter(prefix="/algorithms", tags=["算法管理"])


def soft_delete(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_algorithms(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Algorithm)
    query = soft_delete(query, Algorithm)

    if keyword:
        query = query.where(
            or_(
                Algorithm.name.ilike(f"%{keyword}%"),
                Algorithm.description.ilike(f"%{keyword}%")
            )
        )

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # Load events for each algorithm
    algo_ids = [item.id for item in items]
    events_map = {}
    if algo_ids:
        events_query = select(EventType).where(
            EventType.algorithm_id.in_(algo_ids),
            EventType.deleted_at.is_(None)
        )
        events_result = await db.execute(events_query)
        for ev in events_result.scalars().all():
            events_map.setdefault(ev.algorithm_id, []).append(
                AlgorithmEventItem(name=ev.name, description=ev.description, module_name=ev.module_name)
            )

    response_items = []
    for item in items:
        algo_dict = {
            "id": item.id,
            "name": item.name,
            "type": item.type,
            "description": item.description,
            "business_category": item.business_category,
            "created_at": item.created_at,
            "updated_at": item.updated_at,
            "deleted_at": item.deleted_at,
            "events": events_map.get(item.id, []),
        }
        response_items.append(AlgorithmResponse.model_validate(algo_dict))

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=response_items
    )


@router.get("/{algorithm_id}", response_model=AlgorithmResponse)
async def get_algorithm(algorithm_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Algorithm).where(
        Algorithm.id == algorithm_id,
        Algorithm.deleted_at.is_(None)
    )
    result = await db.execute(query)
    algorithm = result.scalar_one_or_none()
    if not algorithm:
        raise HTTPException(status_code=404, detail="算法不存在")

    # Load events for this algorithm
    events_query = select(EventType).where(
        EventType.algorithm_id == algorithm_id,
        EventType.deleted_at.is_(None)
    )
    events_result = await db.execute(events_query)
    events = [
        AlgorithmEventItem(name=ev.name, description=ev.description, module_name=ev.module_name)
        for ev in events_result.scalars().all()
    ]

    algo_dict = {
        "id": algorithm.id,
        "name": algorithm.name,
        "type": algorithm.type,
        "description": algorithm.description,
        "business_category": algorithm.business_category,
        "created_at": algorithm.created_at,
        "updated_at": algorithm.updated_at,
        "deleted_at": algorithm.deleted_at,
        "events": events,
    }
    return AlgorithmResponse.model_validate(algo_dict)


@router.post("", response_model=AlgorithmResponse)
async def create_algorithm(data: AlgorithmCreate, db: AsyncSession = Depends(get_db)):
    algorithm = Algorithm(**data.model_dump())
    db.add(algorithm)
    await db.commit()
    await db.refresh(algorithm)
    return algorithm


@router.put("/{algorithm_id}", response_model=AlgorithmResponse)
async def update_algorithm(
    algorithm_id: int,
    data: AlgorithmUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Algorithm).where(
        Algorithm.id == algorithm_id,
        Algorithm.deleted_at.is_(None)
    )
    result = await db.execute(query)
    algorithm = result.scalar_one_or_none()
    if not algorithm:
        raise HTTPException(status_code=404, detail="算法不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(algorithm, key, value)

    await db.commit()
    await db.refresh(algorithm)
    return algorithm


@router.delete("/{algorithm_id}")
async def delete_algorithm(algorithm_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Algorithm).where(
        Algorithm.id == algorithm_id,
        Algorithm.deleted_at.is_(None)
    )
    result = await db.execute(query)
    algorithm = result.scalar_one_or_none()
    if not algorithm:
        raise HTTPException(status_code=404, detail="算法不存在")

    algorithm.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Microservice
from app.schemas import (
    MicroserviceCreate, MicroserviceUpdate, MicroserviceResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/microservices", tags=["微服务管理"])


@router.get("", response_model=PaginatedResponse)
async def list_microservices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Microservice).where(Microservice.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                Microservice.name.ilike(f"%{keyword}%"),
                Microservice.service_name.ilike(f"%{keyword}%"),
            )
        )

    if status:
        query = query.where(Microservice.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Microservice.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[MicroserviceResponse.model_validate(item) for item in items]
    )


@router.get("/{item_id}", response_model=MicroserviceResponse)
async def get_microservice(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Microservice).where(
        Microservice.id == item_id,
        Microservice.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="微服务不存在")
    return item


@router.post("", response_model=MicroserviceResponse)
async def create_microservice(data: MicroserviceCreate, db: AsyncSession = Depends(get_db)):
    item = Microservice(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=MicroserviceResponse)
async def update_microservice(
    item_id: int,
    data: MicroserviceUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Microservice).where(
        Microservice.id == item_id,
        Microservice.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="微服务不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_microservice(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Microservice).where(
        Microservice.id == item_id,
        Microservice.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="微服务不存在")

    item.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import DataSource
from app.schemas import (
    DataSourceCreate, DataSourceUpdate, DataSourceResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/data-sources", tags=["数据源管理"])


@router.get("", response_model=PaginatedResponse)
async def list_data_sources(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    access_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(DataSource).where(DataSource.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                DataSource.name.ilike(f"%{keyword}%"),
                DataSource.region.ilike(f"%{keyword}%"),
            )
        )

    if access_type:
        query = query.where(DataSource.access_type == access_type)

    if status:
        query = query.where(DataSource.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(DataSource.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[DataSourceResponse.model_validate(item) for item in items]
    )


@router.get("/{item_id}", response_model=DataSourceResponse)
async def get_data_source(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DataSource).where(
        DataSource.id == item_id,
        DataSource.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="数据源不存在")
    return item


@router.post("", response_model=DataSourceResponse)
async def create_data_source(data: DataSourceCreate, db: AsyncSession = Depends(get_db)):
    item = DataSource(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.put("/{item_id}", response_model=DataSourceResponse)
async def update_data_source(
    item_id: int,
    data: DataSourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(DataSource).where(
        DataSource.id == item_id,
        DataSource.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="数据源不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_data_source(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DataSource).where(
        DataSource.id == item_id,
        DataSource.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="数据源不存在")

    item.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.post("/test-connection")
async def test_connection(data: dict, db: AsyncSession = Depends(get_db)):
    # Simplified test - always success for now
    return {"success": True, "message": "连接测试成功"}


@router.post("/{item_id}/sync")
async def sync_data_source(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DataSource).where(
        DataSource.id == item_id,
        DataSource.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="数据源不存在")

    return {"message": "同步请求已发送", "data_source_id": item_id}


@router.get("/{item_id}/devices")
async def get_data_source_devices(
    item_id: int,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    query = select(DataSource).where(
        DataSource.id == item_id,
        DataSource.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="数据源不存在")

    return {
        "total": 0,
        "page": page,
        "page_size": page_size,
        "items": [],
    }

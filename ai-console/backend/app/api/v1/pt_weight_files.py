from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.pt_weight_file import PTWeightFile
from app.schemas import (
    PTWeightFileCreate, PTWeightFileUpdate, PTWeightFileResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/pt-weight-files", tags=["PT权重文件管理"])


@router.get("", response_model=PaginatedResponse)
async def list_pt_weight_files(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(PTWeightFile).where(PTWeightFile.deleted_at.is_(None))

    if keyword:
        query = query.where(PTWeightFile.name.ilike(f"%{keyword}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(PTWeightFile.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[PTWeightFileResponse.model_validate(item) for item in items]
    )


@router.get("/{item_id}", response_model=PTWeightFileResponse)
async def get_pt_weight_file(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PTWeightFile).where(
        PTWeightFile.id == item_id,
        PTWeightFile.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="PT权重文件不存在")
    return PTWeightFileResponse.model_validate(item)


@router.post("", response_model=PTWeightFileResponse)
async def create_pt_weight_file(data: PTWeightFileCreate, db: AsyncSession = Depends(get_db)):
    item = PTWeightFile(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return PTWeightFileResponse.model_validate(item)


@router.put("/{item_id}", response_model=PTWeightFileResponse)
async def update_pt_weight_file(
    item_id: int,
    data: PTWeightFileUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(PTWeightFile).where(
        PTWeightFile.id == item_id,
        PTWeightFile.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="PT权重文件不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return PTWeightFileResponse.model_validate(item)


@router.delete("/{item_id}")
async def delete_pt_weight_file(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PTWeightFile).where(
        PTWeightFile.id == item_id,
        PTWeightFile.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="PT权重文件不存在")

    item.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import DisposeTag
from app.schemas import (
    DisposeTagCreate, DisposeTagUpdate, DisposeTagResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/dispose-tags", tags=["处置标签管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_dispose_tags(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取处置标签列表
    - keyword: 搜索标签名称
    """
    query = select(DisposeTag)
    query = soft_delete_query(query, DisposeTag)

    if keyword:
        query = query.where(DisposeTag.tag_name.ilike(f"%{keyword}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(DisposeTag.usage_count.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[DisposeTagResponse.model_validate(item) for item in items]
    )


@router.get("/{tag_id}", response_model=DisposeTagResponse)
async def get_dispose_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DisposeTag).where(
        DisposeTag.id == tag_id,
        DisposeTag.deleted_at.is_(None)
    )
    result = await db.execute(query)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")
    return tag


@router.post("", response_model=DisposeTagResponse)
async def create_dispose_tag(data: DisposeTagCreate, db: AsyncSession = Depends(get_db)):
    tag = DisposeTag(**data.model_dump())
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    return tag


@router.put("/{tag_id}", response_model=DisposeTagResponse)
async def update_dispose_tag(
    tag_id: int,
    data: DisposeTagUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(DisposeTag).where(
        DisposeTag.id == tag_id,
        DisposeTag.deleted_at.is_(None)
    )
    result = await db.execute(query)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(tag, key, value)

    await db.commit()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}")
async def delete_dispose_tag(tag_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DisposeTag).where(
        DisposeTag.id == tag_id,
        DisposeTag.deleted_at.is_(None)
    )
    result = await db.execute(query)
    tag = result.scalar_one_or_none()
    if not tag:
        raise HTTPException(status_code=404, detail="标签不存在")

    tag.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}
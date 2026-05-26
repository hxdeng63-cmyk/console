from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import License
from app.schemas import (
    LicenseCreate, LicenseUpdate, LicenseResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/licenses", tags=["授权管理"])


@router.get("", response_model=PaginatedResponse)
async def list_licenses(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(License).where(License.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                License.license_key.ilike(f"%{keyword}%"),
                License.type.ilike(f"%{keyword}%"),
            )
        )

    if status:
        query = query.where(License.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(License.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[LicenseResponse.model_validate(item) for item in items]
    )


@router.get("/info", response_model=dict)
async def get_license_info(db: AsyncSession = Depends(get_db)):
    query = select(License).where(License.deleted_at.is_(None), License.status == "active")
    result = await db.execute(query)
    items = result.scalars().all()
    total_limit = sum(item.device_limit for item in items)
    total_used = sum(item.used_count for item in items)
    return {
        "total_limit": total_limit,
        "total_used": total_used,
        "remaining": total_limit - total_used,
    }


@router.get("/{item_id}", response_model=LicenseResponse)
async def get_license(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(License).where(
        License.id == item_id,
        License.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="授权不存在")
    return item


@router.post("", response_model=LicenseResponse)
async def create_license(data: LicenseCreate, db: AsyncSession = Depends(get_db)):
    item = License(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.post("/verify")
async def verify_license(data: dict, db: AsyncSession = Depends(get_db)):
    # Simplified verification - always valid for now
    return {"valid": True, "message": "授权验证通过"}


@router.put("/{item_id}", response_model=LicenseResponse)
async def update_license(
    item_id: int,
    data: LicenseUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(License).where(
        License.id == item_id,
        License.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="授权不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}")
async def delete_license(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(License).where(
        License.id == item_id,
        License.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="授权不存在")

    item.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}

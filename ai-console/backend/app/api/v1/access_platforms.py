from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import AccessPlatform
from app.schemas import (
    AccessPlatformCreate, AccessPlatformUpdate, AccessPlatformResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/platforms", tags=["接入平台管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_access_platforms(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    platform_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取接入平台列表
    - keyword: 搜索平台名称
    - platform_type: 平台类型枚举筛选（GB28181/ONVIF/RTSP/RTMP）
    - status: 状态筛选
    """
    query = select(AccessPlatform)
    query = soft_delete_query(query, AccessPlatform)

    if keyword:
        query = query.where(AccessPlatform.name.ilike(f"%{keyword}%"))

    if platform_type:
        # Validate platform type enum
        valid_types = ["GB28181", "ONVIF", "RTSP", "RTMP"]
        if platform_type.upper() not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"platform_type 必须是以下之一: {', '.join(valid_types)}"
            )
        query = query.where(AccessPlatform.type == platform_type.upper())

    if status:
        query = query.where(AccessPlatform.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(AccessPlatform.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[AccessPlatformResponse.model_validate(item) for item in items]
    )


@router.get("/{platform_id}", response_model=AccessPlatformResponse)
async def get_access_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    query = select(AccessPlatform).where(
        AccessPlatform.id == platform_id,
        AccessPlatform.deleted_at.is_(None)
    )
    result = await db.execute(query)
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    return platform


@router.post("", response_model=AccessPlatformResponse)
async def create_access_platform(data: AccessPlatformCreate, db: AsyncSession = Depends(get_db)):
    # Validate platform type
    valid_types = ["GB28181", "ONVIF", "RTSP", "RTMP"]
    if data.type.upper() not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"type 必须是以下之一: {', '.join(valid_types)}"
        )

    platform = AccessPlatform(**data.model_dump())
    db.add(platform)
    await db.commit()
    await db.refresh(platform)
    return platform


@router.put("/{platform_id}", response_model=AccessPlatformResponse)
async def update_access_platform(
    platform_id: int,
    data: AccessPlatformUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(AccessPlatform).where(
        AccessPlatform.id == platform_id,
        AccessPlatform.deleted_at.is_(None)
    )
    result = await db.execute(query)
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")

    # Validate platform type if provided
    if data.type:
        valid_types = ["GB28181", "ONVIF", "RTSP", "RTMP"]
        if data.type.upper() not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"type 必须是以下之一: {', '.join(valid_types)}"
            )

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(platform, key, value)

    await db.commit()
    await db.refresh(platform)
    return platform


@router.delete("/{platform_id}")
async def delete_access_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    query = select(AccessPlatform).where(
        AccessPlatform.id == platform_id,
        AccessPlatform.deleted_at.is_(None)
    )
    result = await db.execute(query)
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")

    platform.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.post("/{platform_id}/sync")
async def sync_platform(platform_id: int, db: AsyncSession = Depends(get_db)):
    """同步平台设备"""
    query = select(AccessPlatform).where(
        AccessPlatform.id == platform_id,
        AccessPlatform.deleted_at.is_(None)
    )
    result = await db.execute(query)
    platform = result.scalar_one_or_none()
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")

    # 实际同步逻辑由具体实现决定，这里返回成功消息
    return {"message": "同步请求已发送", "platform_id": platform_id}
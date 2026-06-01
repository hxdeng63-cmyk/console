from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.video_setting import VideoSetting
from app.models.organization import Organization
from app.models.device import Device
from app.schemas import (
    VideoSettingCreate, VideoSettingUpdate, VideoSettingResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/video-settings", tags=["录像设置管理"])


async def _enrich_video_setting(item: VideoSetting, db: AsyncSession) -> dict:
    """Enrich VideoSetting with org name and device info."""
    data = VideoSettingResponse.model_validate(item).model_dump()
    if item.org_id:
        org = await db.get(Organization, item.org_id)
        if org:
            data["org_name"] = org.name

    # Get device info from device_ids
    device_ids = item.device_ids or []
    if device_ids:
        devices_query = select(Device).where(
            Device.id.in_(device_ids),
            Device.deleted_at.is_(None)
        )
        devices_result = await db.execute(devices_query)
        devices = devices_result.scalars().all()
        data["device_names"] = [d.name for d in devices]
    else:
        data["device_names"] = []

    return data


@router.get("", response_model=PaginatedResponse)
async def list_video_settings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    org_id: Optional[int] = None,
    status: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(VideoSetting).where(VideoSetting.deleted_at.is_(None))

    if org_id is not None:
        query = query.where(VideoSetting.org_id == org_id)
    if status is not None:
        query = query.where(VideoSetting.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(VideoSetting.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    enriched = [await _enrich_video_setting(item, db) for item in items]

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=enriched
    )


@router.get("/{item_id}", response_model=VideoSettingResponse)
async def get_video_setting(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(VideoSetting).where(
        VideoSetting.id == item_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="录像设置不存在")
    return await _enrich_video_setting(item, db)


@router.post("", response_model=VideoSettingResponse)
async def create_video_setting(data: VideoSettingCreate, db: AsyncSession = Depends(get_db)):
    # Check if org exists
    org = await db.get(Organization, data.org_id)
    if not org:
        raise HTTPException(status_code=404, detail="公司不存在")

    # Check if video_setting already exists for this org
    existing_query = select(VideoSetting).where(
        VideoSetting.org_id == data.org_id,
        VideoSetting.deleted_at.is_(None)
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该公司已配置录像设置")

    item = VideoSetting(**data.model_dump())
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return await _enrich_video_setting(item, db)


@router.put("/{item_id}", response_model=VideoSettingResponse)
async def update_video_setting(
    item_id: int,
    data: VideoSettingUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(VideoSetting).where(
        VideoSetting.id == item_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)
    return await _enrich_video_setting(item, db)


@router.delete("/{item_id}")
async def delete_video_setting(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(VideoSetting).where(
        VideoSetting.id == item_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    item.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.put("/{item_id}/status")
async def toggle_video_setting_status(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    query = select(VideoSetting).where(
        VideoSetting.id == item_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    item.status = not item.status
    await db.commit()
    await db.refresh(item)
    return {"status": item.status}

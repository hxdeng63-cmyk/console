from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, join
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import VideoSetting, Device, Organization, Region
from app.schemas import (
    VideoSettingCreate, VideoSettingUpdate, VideoSettingResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/video-settings", tags=["录像设置管理"])


async def get_video_setting_with_details(db: AsyncSession, video_setting_id: int) -> Optional[dict]:
    """Get video setting with device, org, and region details"""
    query = select(
        VideoSetting, Device.name.label("device_name"), Device.status.label("device_status"),
        Device.org_id, Organization.name.label("org_name"),
        Device.region_id, Region.name.label("region_name")
    ).select_from(
        VideoSetting
    ).join(
        Device, VideoSetting.device_id == Device.id
    ).outerjoin(
        Organization, Device.org_id == Organization.id
    ).outerjoin(
        Region, Device.region_id == Region.id
    ).where(
        VideoSetting.id == video_setting_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    row = result.first()
    return row


@router.get("", response_model=PaginatedResponse)
async def list_video_settings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    org_id: Optional[int] = None,
    region_id: Optional[int] = None,
    device_name: Optional[str] = None,
    event_type: Optional[str] = None,
    status: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取录像设置列表
    - org_id: 所属公司ID筛选
    - region_id: 所属区域ID筛选
    - device_name: 设备名称搜索
    - event_type: 事件类型筛选
    - status: 启用/禁用状态筛选
    """
    base_query = select(
        VideoSetting, Device.name.label("device_name"), Device.status.label("device_status"),
        Device.org_id, Organization.name.label("org_name"),
        Device.region_id, Region.name.label("region_name")
    ).select_from(
        VideoSetting
    ).join(
        Device, VideoSetting.device_id == Device.id
    ).outerjoin(
        Organization, Device.org_id == Organization.id
    ).outerjoin(
        Region, Device.region_id == Region.id
    ).where(
        VideoSetting.deleted_at.is_(None)
    )

    if status is not None:
        base_query = base_query.where(VideoSetting.status == status)
    if org_id is not None:
        base_query = base_query.where(Device.org_id == org_id)
    if region_id is not None:
        base_query = base_query.where(Device.region_id == region_id)
    if device_name:
        base_query = base_query.where(Device.name.ilike(f"%{device_name}%"))

    # Count total
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Get paginated results
    query = base_query.order_by(VideoSetting.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    rows = result.all()

    items = []
    for row in rows:
        vs = row[0]
        items.append(VideoSettingResponse(
            id=vs.id,
            device_id=vs.device_id,
            event_types=vs.event_types or [],
            record_duration_seconds=vs.record_duration_seconds,
            status=vs.status,
            created_at=vs.created_at,
            updated_at=vs.updated_at,
            deleted_at=vs.deleted_at,
            device_name=row.device_name,
            device_status=row.device_status,
            org_id=row.org_id,
            org_name=row.org_name,
            region_id=row.region_id,
            region_name=row.region_name,
        ))

    return PaginatedResponse(total=total, page=page, page_size=page_size, items=items)


@router.get("/{video_setting_id}", response_model=VideoSettingResponse)
async def get_video_setting(video_setting_id: int, db: AsyncSession = Depends(get_db)):
    row = await get_video_setting_with_details(db, video_setting_id)
    if not row:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    vs = row[0]
    return VideoSettingResponse(
        id=vs.id,
        device_id=vs.device_id,
        event_types=vs.event_types or [],
        record_duration_seconds=vs.record_duration_seconds,
        status=vs.status,
        created_at=vs.created_at,
        updated_at=vs.updated_at,
        deleted_at=vs.deleted_at,
        device_name=row.device_name,
        device_status=row.device_status,
        org_id=row.org_id,
        org_name=row.org_name,
        region_id=row.region_id,
        region_name=row.region_name,
    )


@router.post("", response_model=VideoSettingResponse)
async def create_video_setting(data: VideoSettingCreate, db: AsyncSession = Depends(get_db)):
    # Check if device exists
    device_query = select(Device).where(Device.id == data.device_id, Device.deleted_at.is_(None))
    device_result = await db.execute(device_query)
    device = device_result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    # Check if video_setting already exists for this device
    existing_query = select(VideoSetting).where(
        VideoSetting.device_id == data.device_id,
        VideoSetting.deleted_at.is_(None)
    )
    existing_result = await db.execute(existing_query)
    if existing_result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="该设备已配置录像设置")

    video_setting = VideoSetting(**data.model_dump())
    db.add(video_setting)
    await db.commit()
    await db.refresh(video_setting)

    # Get details
    row = await get_video_setting_with_details(db, video_setting.id)
    if not row:
        raise HTTPException(status_code=500, detail="创建成功但无法获取详情")

    vs = row[0]
    return VideoSettingResponse(
        id=vs.id,
        device_id=vs.device_id,
        event_types=vs.event_types or [],
        record_duration_seconds=vs.record_duration_seconds,
        status=vs.status,
        created_at=vs.created_at,
        updated_at=vs.updated_at,
        deleted_at=vs.deleted_at,
        device_name=row.device_name,
        device_status=row.device_status,
        org_id=row.org_id,
        org_name=row.org_name,
        region_id=row.region_id,
        region_name=row.region_name,
    )


@router.put("/{video_setting_id}", response_model=VideoSettingResponse)
async def update_video_setting(
    video_setting_id: int,
    data: VideoSettingUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(VideoSetting).where(
        VideoSetting.id == video_setting_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    video_setting = result.scalar_one_or_none()
    if not video_setting:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(video_setting, key, value)

    await db.commit()

    row = await get_video_setting_with_details(db, video_setting_id)
    if not row:
        raise HTTPException(status_code=500, detail="更新成功但无法获取详情")

    vs = row[0]
    return VideoSettingResponse(
        id=vs.id,
        device_id=vs.device_id,
        event_types=vs.event_types or [],
        record_duration_seconds=vs.record_duration_seconds,
        status=vs.status,
        created_at=vs.created_at,
        updated_at=vs.updated_at,
        deleted_at=vs.deleted_at,
        device_name=row.device_name,
        device_status=row.device_status,
        org_id=row.org_id,
        org_name=row.org_name,
        region_id=row.region_id,
        region_name=row.region_name,
    )


@router.delete("/{video_setting_id}")
async def delete_video_setting(video_setting_id: int, db: AsyncSession = Depends(get_db)):
    query = select(VideoSetting).where(
        VideoSetting.id == video_setting_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    video_setting = result.scalar_one_or_none()
    if not video_setting:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    video_setting.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.put("/{video_setting_id}/status")
async def toggle_video_setting_status(
    video_setting_id: int,
    status: bool = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """切换录像设置启用/禁用状态"""
    query = select(VideoSetting).where(
        VideoSetting.id == video_setting_id,
        VideoSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    video_setting = result.scalar_one_or_none()
    if not video_setting:
        raise HTTPException(status_code=404, detail="录像设置不存在")

    video_setting.status = status
    await db.commit()
    return {"message": "状态更新成功", "status": status}

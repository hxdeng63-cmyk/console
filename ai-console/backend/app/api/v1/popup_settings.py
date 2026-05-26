from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import PopupSetting
from app.schemas import (
    PopupSettingCreate, PopupSettingUpdate, PopupSettingResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/popup-settings", tags=["弹窗设置管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_popup_settings(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取弹窗设置列表
    - keyword: 搜索配置
    - is_active: 是否激活筛选
    """
    query = select(PopupSetting)
    query = soft_delete_query(query, PopupSetting)

    if is_active is not None:
        query = query.where(PopupSetting.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(PopupSetting.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[PopupSettingResponse.model_validate(item) for item in items]
    )


@router.get("/{setting_id}", response_model=PopupSettingResponse)
async def get_popup_setting(setting_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PopupSetting).where(
        PopupSetting.id == setting_id,
        PopupSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")
    return setting


@router.post("", response_model=PopupSettingResponse)
async def create_popup_setting(data: PopupSettingCreate, db: AsyncSession = Depends(get_db)):
    setting = PopupSetting(**data.model_dump())
    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    return setting


@router.put("/{setting_id}", response_model=PopupSettingResponse)
async def update_popup_setting(
    setting_id: int,
    data: PopupSettingUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(PopupSetting).where(
        PopupSetting.id == setting_id,
        PopupSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(setting, key, value)

    await db.commit()
    await db.refresh(setting)
    return setting


@router.delete("/{setting_id}")
async def delete_popup_setting(setting_id: int, db: AsyncSession = Depends(get_db)):
    query = select(PopupSetting).where(
        PopupSetting.id == setting_id,
        PopupSetting.deleted_at.is_(None)
    )
    result = await db.execute(query)
    setting = result.scalar_one_or_none()
    if not setting:
        raise HTTPException(status_code=404, detail="设置不存在")

    setting.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}
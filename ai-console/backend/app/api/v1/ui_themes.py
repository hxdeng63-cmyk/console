from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import UITheme
from app.schemas import (
    UIThemeCreate, UIThemeUpdate, UIThemeResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/ui-themes", tags=["UI主题管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_ui_themes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    platform: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取UI主题列表
    - keyword: 搜索主题名称
    - platform: 平台筛选
    - is_active: 是否激活筛选
    """
    query = select(UITheme)
    query = soft_delete_query(query, UITheme)

    if keyword:
        query = query.where(UITheme.name.ilike(f"%{keyword}%"))

    if platform:
        query = query.where(UITheme.platform == platform)

    if is_active is not None:
        query = query.where(UITheme.is_active == is_active)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(UITheme.is_active.desc(), UITheme.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[UIThemeResponse.model_validate(item) for item in items]
    )


@router.get("/{theme_id}", response_model=UIThemeResponse)
async def get_ui_theme(theme_id: int, db: AsyncSession = Depends(get_db)):
    query = select(UITheme).where(
        UITheme.id == theme_id,
        UITheme.deleted_at.is_(None)
    )
    result = await db.execute(query)
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")
    return theme


@router.post("", response_model=UIThemeResponse)
async def create_ui_theme(data: UIThemeCreate, db: AsyncSession = Depends(get_db)):
    theme = UITheme(**data.model_dump())
    db.add(theme)
    await db.commit()
    await db.refresh(theme)
    return theme


@router.put("/{theme_id}", response_model=UIThemeResponse)
async def update_ui_theme(
    theme_id: int,
    data: UIThemeUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(UITheme).where(
        UITheme.id == theme_id,
        UITheme.deleted_at.is_(None)
    )
    result = await db.execute(query)
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(theme, key, value)

    await db.commit()
    await db.refresh(theme)
    return theme


@router.delete("/{theme_id}")
async def delete_ui_theme(theme_id: int, db: AsyncSession = Depends(get_db)):
    query = select(UITheme).where(
        UITheme.id == theme_id,
        UITheme.deleted_at.is_(None)
    )
    result = await db.execute(query)
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    theme.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.post("/{theme_id}/activate")
async def activate_ui_theme(theme_id: int, db: AsyncSession = Depends(get_db)):
    """激活指定主题（同时停用其他主题）"""
    query = select(UITheme).where(
        UITheme.id == theme_id,
        UITheme.deleted_at.is_(None)
    )
    result = await db.execute(query)
    theme = result.scalar_one_or_none()
    if not theme:
        raise HTTPException(status_code=404, detail="主题不存在")

    # 停用所有其他主题
    all_themes_query = select(UITheme).where(UITheme.deleted_at.is_(None))
    all_result = await db.execute(all_themes_query)
    all_themes = all_result.scalars().all()
    for t in all_themes:
        t.is_active = False

    # 激活指定主题
    theme.is_active = True
    await db.commit()
    return {"message": "主题已激活"}
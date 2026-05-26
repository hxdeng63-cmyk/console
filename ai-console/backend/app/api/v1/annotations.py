from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Annotation, Preset
from app.schemas import (
    AnnotationCreate, AnnotationUpdate, AnnotationResponse,
    PresetCreate, PresetUpdate, PresetResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/annotations", tags=["标注管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


# ============= Annotation APIs =============

@router.get("", response_model=PaginatedResponse)
async def list_annotations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    deployment_id: Optional[int] = None,
    device_id: Optional[int] = None,
    annotation_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取标注列表
    - keyword: 搜索标注名称
    - deployment_id: 布控任务ID筛选
    - device_id: 设备ID筛选
    - annotation_type: 标注类型筛选（monitoring/forbidden）
    """
    query = select(Annotation)
    query = soft_delete_query(query, Annotation)

    if keyword:
        query = query.where(Annotation.name.ilike(f"%{keyword}%"))

    if deployment_id is not None:
        query = query.where(Annotation.deployment_id == deployment_id)

    if device_id is not None:
        query = query.where(Annotation.device_id == device_id)

    if annotation_type:
        query = query.where(Annotation.type == annotation_type)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[AnnotationResponse.model_validate(item) for item in items]
    )


@router.get("/{annotation_id}", response_model=AnnotationResponse)
async def get_annotation(annotation_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Annotation).where(
        Annotation.id == annotation_id,
        Annotation.deleted_at.is_(None)
    )
    result = await db.execute(query)
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")
    return annotation


@router.post("", response_model=AnnotationResponse)
async def create_annotation(data: AnnotationCreate, db: AsyncSession = Depends(get_db)):
    annotation = Annotation(**data.model_dump())
    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    return annotation


@router.put("/{annotation_id}", response_model=AnnotationResponse)
async def update_annotation(
    annotation_id: int,
    data: AnnotationUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Annotation).where(
        Annotation.id == annotation_id,
        Annotation.deleted_at.is_(None)
    )
    result = await db.execute(query)
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(annotation, key, value)

    await db.commit()
    await db.refresh(annotation)
    return annotation


@router.delete("/{annotation_id}")
async def delete_annotation(annotation_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Annotation).where(
        Annotation.id == annotation_id,
        Annotation.deleted_at.is_(None)
    )
    result = await db.execute(query)
    annotation = result.scalar_one_or_none()
    if not annotation:
        raise HTTPException(status_code=404, detail="标注不存在")

    annotation.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


# ============= Preset APIs =============

@router.get("/presets", response_model=PaginatedResponse)
async def list_presets(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    device_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取预置点列表
    - keyword: 搜索预置点名称
    - device_id: 设备ID筛选
    """
    query = select(Preset)
    query = soft_delete_query(query, Preset)

    if keyword:
        query = query.where(Preset.name.ilike(f"%{keyword}%"))

    if device_id is not None:
        query = query.where(Preset.device_id == device_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[PresetResponse.model_validate(item) for item in items]
    )


@router.get("/presets/{preset_id}", response_model=PresetResponse)
async def get_preset(preset_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Preset).where(
        Preset.id == preset_id,
        Preset.deleted_at.is_(None)
    )
    result = await db.execute(query)
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="预置点不存在")
    return preset


@router.post("/presets", response_model=PresetResponse)
async def create_preset(data: PresetCreate, db: AsyncSession = Depends(get_db)):
    preset = Preset(**data.model_dump())
    db.add(preset)
    await db.commit()
    await db.refresh(preset)
    return preset


@router.put("/presets/{preset_id}", response_model=PresetResponse)
async def update_preset(
    preset_id: int,
    data: PresetUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Preset).where(
        Preset.id == preset_id,
        Preset.deleted_at.is_(None)
    )
    result = await db.execute(query)
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="预置点不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(preset, key, value)

    await db.commit()
    await db.refresh(preset)
    return preset


@router.delete("/presets/{preset_id}")
async def delete_preset(preset_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Preset).where(
        Preset.id == preset_id,
        Preset.deleted_at.is_(None)
    )
    result = await db.execute(query)
    preset = result.scalar_one_or_none()
    if not preset:
        raise HTTPException(status_code=404, detail="预置点不存在")

    preset.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}
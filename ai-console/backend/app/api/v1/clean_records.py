from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import CleanRecord
from app.schemas import (
    CleanRecordCreate, CleanRecordUpdate, CleanRecordResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/clean-records", tags=["清理记录管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_clean_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取清理记录列表
    - type: 类型筛选
    - status: 状态筛选
    """
    query = select(CleanRecord)
    query = soft_delete_query(query, CleanRecord)

    if type:
        query = query.where(CleanRecord.type == type)

    if status:
        query = query.where(CleanRecord.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(CleanRecord.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[CleanRecordResponse.model_validate(item) for item in items]
    )


@router.get("/{record_id}", response_model=CleanRecordResponse)
async def get_clean_record(record_id: int, db: AsyncSession = Depends(get_db)):
    query = select(CleanRecord).where(
        CleanRecord.id == record_id,
        CleanRecord.deleted_at.is_(None)
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="清理记录不存在")
    return record


@router.post("", response_model=CleanRecordResponse)
async def create_clean_record(data: CleanRecordCreate, db: AsyncSession = Depends(get_db)):
    record = CleanRecord(**data.model_dump())
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.put("/{record_id}", response_model=CleanRecordResponse)
async def update_clean_record(
    record_id: int,
    data: CleanRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(CleanRecord).where(
        CleanRecord.id == record_id,
        CleanRecord.deleted_at.is_(None)
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="清理记录不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/{record_id}")
async def delete_clean_record(record_id: int, db: AsyncSession = Depends(get_db)):
    query = select(CleanRecord).where(
        CleanRecord.id == record_id,
        CleanRecord.deleted_at.is_(None)
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="清理记录不存在")

    record.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.post("/execute", response_model=CleanRecordResponse)
async def execute_clean(
    data: dict,
    db: AsyncSession = Depends(get_db)
):
    """手动执行数据清理任务

    Request body:
        dimension: str - 清理维度，可选 "all" | "warning_event" | "video_file"，默认 "all"
    """
    from app.services.cleanup_service import execute_cleanup

    dimension = data.get("dimension", "all")
    if dimension not in ("all", "warning_event", "video_file"):
        raise HTTPException(status_code=400, detail="dimension 参数无效")

    record = await execute_cleanup(db, dimension=dimension)
    return record


@router.get("/status/{record_id}", response_model=CleanRecordResponse)
async def get_clean_status(record_id: int, db: AsyncSession = Depends(get_db)):
    """查询清理任务状态"""
    query = select(CleanRecord).where(
        CleanRecord.id == record_id,
        CleanRecord.deleted_at.is_(None)
    )
    result = await db.execute(query)
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="清理记录不存在")
    return record

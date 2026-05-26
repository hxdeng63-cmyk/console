from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import OperationLog
from app.schemas import (
    OperationLogCreate, OperationLogUpdate, OperationLogResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/operation-logs", tags=["操作日志"])


@router.get("", response_model=PaginatedResponse)
async def list_operation_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    module: Optional[str] = None,
    username: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(OperationLog).where(OperationLog.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                OperationLog.username.ilike(f"%{keyword}%"),
                OperationLog.action.ilike(f"%{keyword}%"),
            )
        )

    if module:
        query = query.where(OperationLog.module == module)

    if username:
        query = query.where(OperationLog.username.ilike(f"%{username}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(OperationLog.action_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[OperationLogResponse.model_validate(item) for item in items]
    )


@router.get("/{item_id}", response_model=OperationLogResponse)
async def get_operation_log(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(OperationLog).where(
        OperationLog.id == item_id,
        OperationLog.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="日志不存在")
    return item


@router.get("/export")
async def export_operation_logs(
    keyword: Optional[str] = None,
    module: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(OperationLog).where(OperationLog.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                OperationLog.username.ilike(f"%{keyword}%"),
                OperationLog.action.ilike(f"%{keyword}%"),
            )
        )

    if module:
        query = query.where(OperationLog.module == module)

    result = await db.execute(query)
    items = result.scalars().all()
    return {
        "items": [OperationLogResponse.model_validate(item) for item in items],
        "total": len(items),
    }


@router.post("/batch-delete")
async def batch_delete_operation_logs(data: dict, db: AsyncSession = Depends(get_db)):
    ids = data.get("ids", [])
    if not ids:
        raise HTTPException(status_code=400, detail="未提供ID列表")

    query = select(OperationLog).where(
        OperationLog.id.in_(ids),
        OperationLog.deleted_at.is_(None)
    )
    result = await db.execute(query)
    items = result.scalars().all()

    for item in items:
        item.deleted_at = datetime.utcnow()

    await db.commit()
    return {"message": f"已删除 {len(items)} 条日志"}


@router.delete("/{item_id}")
async def delete_operation_log(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(OperationLog).where(
        OperationLog.id == item_id,
        OperationLog.deleted_at.is_(None)
    )
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="日志不存在")

    item.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}

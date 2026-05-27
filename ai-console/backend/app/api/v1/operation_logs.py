from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import OperationLog
from app.models.user import User
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
    operator: Optional[str] = None,
    ip: Optional[str] = None,
    method: Optional[str] = None,
    path: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(OperationLog, User.real_name)
        .outerjoin(User, User.username == OperationLog.username)
        .where(OperationLog.deleted_at.is_(None))
    )

    if keyword:
        query = query.where(
            or_(
                OperationLog.username.ilike(f"%{keyword}%"),
                OperationLog.path.ilike(f"%{keyword}%"),
            )
        )

    if operator:
        query = query.where(OperationLog.username.ilike(f"%{operator}%"))

    if ip:
        query = query.where(OperationLog.ip.ilike(f"%{ip}%"))

    if method:
        query = query.where(OperationLog.method == method)

    if path:
        query = query.where(OperationLog.path.ilike(f"%{path}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(OperationLog.action_time.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    items = []
    for log, real_name in result.all():
        data = OperationLogResponse.model_validate(log).model_dump()
        data["real_name"] = real_name or log.username or ""
        items.append(data)

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
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
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(OperationLog, User.real_name)
        .outerjoin(User, User.username == OperationLog.username)
        .where(OperationLog.deleted_at.is_(None))
    )

    if keyword:
        query = query.where(
            or_(
                OperationLog.username.ilike(f"%{keyword}%"),
                OperationLog.path.ilike(f"%{keyword}%"),
            )
        )

    if description:
        query = query.where(OperationLog.description.ilike(f"%{description}%"))

    result = await db.execute(query)
    items = []
    for log, real_name in result.all():
        data = OperationLogResponse.model_validate(log).model_dump()
        data["real_name"] = real_name or log.username or ""
        items.append(data)
    return {
        "items": items,
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

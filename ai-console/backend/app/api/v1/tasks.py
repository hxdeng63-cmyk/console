from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Task
from app.schemas import (
    TaskCreate, TaskUpdate, TaskResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/tasks", tags=["任务管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_tasks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    trigger_type: Optional[str] = None,
    algorithm_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取任务列表
    - 支持按 status 筛选
    - keyword: 搜索任务名称
    - trigger_type: 触发类型筛选（cron/event）
    - algorithm_id: 算法ID筛选
    """
    query = select(Task)
    query = soft_delete_query(query, Task)

    if keyword:
        query = query.where(Task.task_name.ilike(f"%{keyword}%"))

    if status:
        query = query.where(Task.status == status)

    if trigger_type:
        query = query.where(Task.trigger_type == trigger_type)

    if algorithm_id is not None:
        query = query.where(Task.algorithm_id == algorithm_id)

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
        items=[TaskResponse.model_validate(item) for item in items]
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    return task


@router.post("", response_model=TaskResponse)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.post("/{task_id}/run")
async def run_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.last_run_time = datetime.utcnow()
    await db.commit()
    return {"message": "任务已触发"}


@router.post("/{task_id}/enable")
async def enable_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = "active"
    await db.commit()
    return {"message": "任务已启用"}


@router.post("/{task_id}/disable")
async def disable_task(task_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Task).where(
        Task.id == task_id,
        Task.deleted_at.is_(None)
    )
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    task.status = "inactive"
    await db.commit()
    return {"message": "任务已禁用"}
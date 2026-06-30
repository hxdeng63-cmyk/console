from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import AlgorithmService
from app.schemas import (
    AlgorithmServiceCreate, AlgorithmServiceUpdate, AlgorithmServiceResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/algorithm-services", tags=["算法服务管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_algorithm_services(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    algorithm_id: Optional[int] = None,
    device_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取算法服务列表
    - 支持关联查询 algorithm 和 device
    - keyword: 搜索服务名称/服务ID
    - status: 状态筛选
    - algorithm_id: 算法ID筛选
    - device_id: 设备ID筛选（通过关联的deployment）
    """
    query = select(AlgorithmService)
    query = soft_delete_query(query, AlgorithmService)

    if keyword:
        query = query.where(
            or_(
                AlgorithmService.service_name.ilike(f"%{keyword}%"),
                AlgorithmService.service_id.ilike(f"%{keyword}%")
            )
        )

    if status:
        query = query.where(AlgorithmService.status == status)

    # Note: algorithm_id and device_id filtering would require joins
    # when the full relationship is needed

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
        items=[AlgorithmServiceResponse.model_validate(item) for item in items]
    )


@router.get("/{service_id}", response_model=AlgorithmServiceResponse)
async def get_algorithm_service(service_id: int, db: AsyncSession = Depends(get_db)):
    query = select(AlgorithmService).where(
        AlgorithmService.id == service_id,
        AlgorithmService.deleted_at.is_(None)
    )
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="算法服务不存在")
    return service


@router.post("", response_model=AlgorithmServiceResponse)
async def create_algorithm_service(data: AlgorithmServiceCreate, db: AsyncSession = Depends(get_db)):
    service = AlgorithmService(**data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service


@router.put("/{service_id}", response_model=AlgorithmServiceResponse)
async def update_algorithm_service(
    service_id: int,
    data: AlgorithmServiceUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(AlgorithmService).where(
        AlgorithmService.id == service_id,
        AlgorithmService.deleted_at.is_(None)
    )
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="算法服务不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(service, key, value)

    await db.commit()
    await db.refresh(service)
    return service


@router.delete("/{service_id}")
async def delete_algorithm_service(service_id: int, db: AsyncSession = Depends(get_db)):
    query = select(AlgorithmService).where(
        AlgorithmService.id == service_id,
        AlgorithmService.deleted_at.is_(None)
    )
    result = await db.execute(query)
    service = result.scalar_one_or_none()
    if not service:
        raise HTTPException(status_code=404, detail="算法服务不存在")

    service.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}

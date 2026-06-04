from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.deployment import Deployment
from app.models.deployment_device import DeploymentDevice
from app.schemas.request.deployment import (
    DeploymentRequest,
    DeploymentResponse,
)

router = APIRouter(prefix="/deployments", tags=["deployments"])


async def _get_device_ids_map(db: AsyncSession, deployment_ids: list[int]) -> dict[int, list[int]]:
    """批量查询 deployment 的关联设备 ID"""
    if not deployment_ids:
        return {}
    stmt = select(DeploymentDevice.deployment_id, DeploymentDevice.device_id).where(
        DeploymentDevice.deployment_id.in_(deployment_ids)
    )
    result = await db.execute(stmt)
    mapping: dict[int, list[int]] = {}
    for dep_id, dev_id in result.all():
        mapping.setdefault(dep_id, []).append(dev_id)
    return mapping


def _build_response(item: Deployment, device_ids: list[int]) -> dict:
    """构建包含 device_ids 的响应字典"""
    return {
        "id": item.id,
        "name": item.name,
        "algorithm_id": item.algorithm_id,
        "service_id": item.service_id,
        "status": item.status,
        "algorithm_status": item.algorithm_status,
        "deployed_at": item.deployed_at,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
        "deleted_at": item.deleted_at,
        "device_ids": device_ids,
        "schedule": item.schedule,
    }


@router.get("", response_model=dict)
async def list_deployments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    algorithm_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Deployment).where(Deployment.deleted_at.is_(None))

    if keyword:
        query = query.where(Deployment.name.ilike(f"%{keyword}%"))
    if status:
        query = query.where(Deployment.status == status)
    if algorithm_id:
        query = query.where(Deployment.algorithm_id == algorithm_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # 批量查询关联设备
    dep_ids = [item.id for item in items]
    device_map = await _get_device_ids_map(db, dep_ids)

    return {
        "items": [DeploymentResponse.model_validate(_build_response(item, device_map.get(item.id, []))) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=DeploymentResponse)
async def get_deployment(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    device_map = await _get_device_ids_map(db, [deployment.id])
    return DeploymentResponse.model_validate(_build_response(deployment, device_map.get(deployment.id, [])))


@router.post("", response_model=DeploymentResponse)
async def create_deployment(data: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    device_ids = data.device_ids or []

    # 创建 Deployment（排除 device_ids）
    dump = data.model_dump(exclude={"device_ids"})
    if not dump.get("name"):
        raise HTTPException(status_code=400, detail="name is required")
    deployment = Deployment(**dump)
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)

    # 批量插入关联
    if device_ids:
        db.add_all([
            DeploymentDevice(deployment_id=deployment.id, device_id=did)
            for did in device_ids
        ])
        await db.commit()

    return DeploymentResponse.model_validate(_build_response(deployment, device_ids))


@router.put("/{item_id}", response_model=DeploymentResponse)
async def update_deployment(item_id: int, data: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    device_ids = data.device_ids or []

    # 更新 Deployment 字段（排除 device_ids，只更新请求中发送的字段）
    for key, value in data.model_dump(exclude={"device_ids"}, exclude_unset=True).items():
        setattr(deployment, key, value)

    await db.commit()
    await db.refresh(deployment)

    # 删除旧关联，插入新关联
    await db.execute(delete(DeploymentDevice).where(DeploymentDevice.deployment_id == item_id))
    if device_ids:
        db.add_all([
            DeploymentDevice(deployment_id=item_id, device_id=did)
            for did in device_ids
        ])
    await db.commit()

    return DeploymentResponse.model_validate(_build_response(deployment, device_ids))


@router.delete("/{item_id}")
async def delete_deployment(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.deleted_at = datetime.utcnow()

    # 硬删除关联
    await db.execute(delete(DeploymentDevice).where(DeploymentDevice.deployment_id == item_id))
    await db.commit()

    return {"message": "Deployment deleted"}
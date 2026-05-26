from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.deployment import Deployment
from app.schemas.request.deployment import (
    DeploymentRequest,
    DeploymentResponse,
)

router = APIRouter(prefix="/deployments", tags=["deployments"])


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

    return {
        "items": [DeploymentResponse.model_validate(item) for item in items],
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
    return DeploymentResponse.model_validate(deployment)


@router.post("", response_model=DeploymentResponse)
async def create_deployment(data: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    deployment = Deployment(**data.model_dump())
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    return DeploymentResponse.model_validate(deployment)


@router.put("/{item_id}", response_model=DeploymentResponse)
async def update_deployment(item_id: int, data: DeploymentRequest, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    for key, value in data.model_dump().items():
        setattr(deployment, key, value)

    await db.commit()
    await db.refresh(deployment)
    return DeploymentResponse.model_validate(deployment)


@router.delete("/{item_id}")
async def delete_deployment(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Deployment).where(Deployment.id == item_id, Deployment.deleted_at.is_(None))
    result = await db.execute(query)
    deployment = result.scalar_one_or_none()
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")

    deployment.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Deployment deleted"}
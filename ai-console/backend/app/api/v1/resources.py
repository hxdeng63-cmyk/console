from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.resource import Resource
from app.schemas.request.user import ResourceRequest, ResourceResponse

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=dict)
async def list_resources(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    resource_group: str = Query(None),
    method: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Resource).where(Resource.deleted_at.is_(None))

    if keyword:
        query = query.where(Resource.resource.ilike(f"%{keyword}%"))
    if resource_group:
        query = query.where(Resource.resource_group == resource_group)
    if method:
        query = query.where(Resource.method == method)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [ResourceResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=ResourceResponse)
async def get_resource(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Resource).where(Resource.id == item_id, Resource.deleted_at.is_(None))
    result = await db.execute(query)
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ResourceResponse.model_validate(resource)


@router.post("", response_model=ResourceResponse)
async def create_resource(data: ResourceRequest, db: AsyncSession = Depends(get_db)):
    resource = Resource(**data.model_dump())
    db.add(resource)
    await db.commit()
    await db.refresh(resource)
    return ResourceResponse.model_validate(resource)


@router.put("/{item_id}", response_model=ResourceResponse)
async def update_resource(item_id: int, data: ResourceRequest, db: AsyncSession = Depends(get_db)):
    query = select(Resource).where(Resource.id == item_id, Resource.deleted_at.is_(None))
    result = await db.execute(query)
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    for key, value in data.model_dump().items():
        setattr(resource, key, value)

    await db.commit()
    await db.refresh(resource)
    return ResourceResponse.model_validate(resource)


@router.delete("/{item_id}")
async def delete_resource(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Resource).where(Resource.id == item_id, Resource.deleted_at.is_(None))
    result = await db.execute(query)
    resource = result.scalar_one_or_none()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Resource deleted"}
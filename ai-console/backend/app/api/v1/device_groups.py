from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.device_group import DeviceGroup
from app.schemas.request.device import DeviceGroupRequest, DeviceGroupResponse, DeviceGroupTreeResponse

router = APIRouter(prefix="/device-groups", tags=["device-groups"])


@router.get("", response_model=dict)
async def list_device_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    parent_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(DeviceGroup).where(DeviceGroup.deleted_at.is_(None))

    if keyword:
        query = query.where(DeviceGroup.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(DeviceGroup.parent_id == parent_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [DeviceGroupResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/tree", response_model=list[DeviceGroupTreeResponse])
async def get_device_group_tree(db: AsyncSession = Depends(get_db)):
    query = select(DeviceGroup).where(
        DeviceGroup.deleted_at.is_(None)
    ).order_by(DeviceGroup.sort)

    result = await db.execute(query)
    all_groups = result.scalars().all()

    group_map = {g.id: DeviceGroupTreeResponse.model_validate(g) for g in all_groups}
    roots = []

    for group in all_groups:
        node = group_map[group.id]
        if group.parent_id and group.parent_id in group_map:
            group_map[group.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/{item_id}", response_model=DeviceGroupResponse)
async def get_device_group(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DeviceGroup).where(DeviceGroup.id == item_id, DeviceGroup.deleted_at.is_(None))
    result = await db.execute(query)
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Device group not found")
    return DeviceGroupResponse.model_validate(group)


@router.post("", response_model=DeviceGroupResponse)
async def create_device_group(data: DeviceGroupRequest, db: AsyncSession = Depends(get_db)):
    group = DeviceGroup(**data.model_dump())
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return DeviceGroupResponse.model_validate(group)


@router.put("/{item_id}", response_model=DeviceGroupResponse)
async def update_device_group(item_id: int, data: DeviceGroupRequest, db: AsyncSession = Depends(get_db)):
    query = select(DeviceGroup).where(DeviceGroup.id == item_id, DeviceGroup.deleted_at.is_(None))
    result = await db.execute(query)
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Device group not found")

    for key, value in data.model_dump().items():
        setattr(group, key, value)

    await db.commit()
    await db.refresh(group)
    return DeviceGroupResponse.model_validate(group)


@router.delete("/{item_id}")
async def delete_device_group(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DeviceGroup).where(DeviceGroup.id == item_id, DeviceGroup.deleted_at.is_(None))
    result = await db.execute(query)
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Device group not found")

    group.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Device group deleted"}
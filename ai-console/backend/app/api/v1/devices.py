from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device import Device
from app.schemas.request.device import DeviceRequest, DeviceResponse

router = APIRouter(prefix="/devices", tags=["devices"])


@router.get("", response_model=dict)
async def list_devices(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    access_type: str = Query(None),
    region_id: int = Query(None),
    org_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Device).where(Device.deleted_at.is_(None))

    if keyword:
        query = query.where(
            or_(
                Device.name.ilike(f"%{keyword}%"),
                Device.device_code.ilike(f"%{keyword}%"),
            )
        )
    if status:
        query = query.where(Device.status == status)
    if access_type:
        query = query.where(Device.access_type == access_type)
    if region_id:
        query = query.where(Device.region_id == region_id)
    if org_id:
        query = query.where(Device.org_id == org_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [DeviceResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=DeviceResponse)
async def get_device(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Device).where(Device.id == item_id, Device.deleted_at.is_(None))
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return DeviceResponse.model_validate(device)


@router.post("", response_model=DeviceResponse)
async def create_device(data: DeviceRequest, db: AsyncSession = Depends(get_db)):
    device = Device(**data.model_dump())
    db.add(device)
    await db.commit()
    await db.refresh(device)
    return DeviceResponse.model_validate(device)


@router.put("/{item_id}", response_model=DeviceResponse)
async def update_device(item_id: int, data: DeviceRequest, db: AsyncSession = Depends(get_db)):
    query = select(Device).where(Device.id == item_id, Device.deleted_at.is_(None))
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    for key, value in data.model_dump().items():
        setattr(device, key, value)

    await db.commit()
    await db.refresh(device)
    return DeviceResponse.model_validate(device)


@router.delete("/{item_id}")
async def delete_device(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Device).where(Device.id == item_id, Device.deleted_at.is_(None))
    result = await db.execute(query)
    device = result.scalar_one_or_none()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Device deleted"}
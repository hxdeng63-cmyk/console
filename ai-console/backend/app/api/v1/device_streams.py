from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device_stream import DeviceStream
from app.schemas.request.device_stream import DeviceStreamRequest, DeviceStreamResponse

router = APIRouter(prefix="/device-streams", tags=["device-streams"])


@router.get("", response_model=dict)
async def list_device_streams(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    device_id: int = Query(None),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(DeviceStream).where(DeviceStream.deleted_at.is_(None))

    if device_id:
        query = query.where(DeviceStream.device_id == device_id)
    if status:
        query = query.where(DeviceStream.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [DeviceStreamResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=DeviceStreamResponse)
async def get_device_stream(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DeviceStream).where(DeviceStream.id == item_id, DeviceStream.deleted_at.is_(None))
    result = await db.execute(query)
    stream = result.scalar_one_or_none()
    if not stream:
        raise HTTPException(status_code=404, detail="Device stream not found")
    return DeviceStreamResponse.model_validate(stream)


@router.post("", response_model=DeviceStreamResponse)
async def create_device_stream(data: DeviceStreamRequest, db: AsyncSession = Depends(get_db)):
    stream = DeviceStream(**data.model_dump())
    db.add(stream)
    await db.commit()
    await db.refresh(stream)
    return DeviceStreamResponse.model_validate(stream)


@router.put("/{item_id}", response_model=DeviceStreamResponse)
async def update_device_stream(item_id: int, data: DeviceStreamRequest, db: AsyncSession = Depends(get_db)):
    query = select(DeviceStream).where(DeviceStream.id == item_id, DeviceStream.deleted_at.is_(None))
    result = await db.execute(query)
    stream = result.scalar_one_or_none()
    if not stream:
        raise HTTPException(status_code=404, detail="Device stream not found")

    for key, value in data.model_dump().items():
        setattr(stream, key, value)

    await db.commit()
    await db.refresh(stream)
    return DeviceStreamResponse.model_validate(stream)


@router.delete("/{item_id}")
async def delete_device_stream(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(DeviceStream).where(DeviceStream.id == item_id, DeviceStream.deleted_at.is_(None))
    result = await db.execute(query)
    stream = result.scalar_one_or_none()
    if not stream:
        raise HTTPException(status_code=404, detail="Device stream not found")

    stream.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Device stream deleted"}
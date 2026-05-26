from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import Firmware
from app.schemas import (
    FirmwareCreate, FirmwareUpdate, FirmwareResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/firmwares", tags=["固件管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_firmwares(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    force_upgrade: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取固件列表
    - keyword: 搜索固件名称/版本
    - force_upgrade: 是否强制升级筛选
    """
    query = select(Firmware)
    query = soft_delete_query(query, Firmware)

    if keyword:
        query = query.where(
            or_(
                Firmware.name.ilike(f"%{keyword}%"),
                Firmware.version.ilike(f"%{keyword}%"),
                Firmware.description.ilike(f"%{keyword}%")
            )
        )

    if force_upgrade is not None:
        query = query.where(Firmware.force_upgrade == force_upgrade)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Firmware.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FirmwareResponse.model_validate(item) for item in items]
    )


@router.get("/{firmware_id}", response_model=FirmwareResponse)
async def get_firmware(firmware_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Firmware).where(
        Firmware.id == firmware_id,
        Firmware.deleted_at.is_(None)
    )
    result = await db.execute(query)
    firmware = result.scalar_one_or_none()
    if not firmware:
        raise HTTPException(status_code=404, detail="固件不存在")
    return firmware


@router.post("", response_model=FirmwareResponse)
async def create_firmware(data: FirmwareCreate, db: AsyncSession = Depends(get_db)):
    firmware = Firmware(**data.model_dump())
    db.add(firmware)
    await db.commit()
    await db.refresh(firmware)
    return firmware


@router.put("/{firmware_id}", response_model=FirmwareResponse)
async def update_firmware(
    firmware_id: int,
    data: FirmwareUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(Firmware).where(
        Firmware.id == firmware_id,
        Firmware.deleted_at.is_(None)
    )
    result = await db.execute(query)
    firmware = result.scalar_one_or_none()
    if not firmware:
        raise HTTPException(status_code=404, detail="固件不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(firmware, key, value)

    await db.commit()
    await db.refresh(firmware)
    return firmware


@router.delete("/{firmware_id}")
async def delete_firmware(firmware_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Firmware).where(
        Firmware.id == firmware_id,
        Firmware.deleted_at.is_(None)
    )
    result = await db.execute(query)
    firmware = result.scalar_one_or_none()
    if not firmware:
        raise HTTPException(status_code=404, detail="固件不存在")

    firmware.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.get("/versions/{device_type}")
async def get_firmware_versions(device_type: str, db: AsyncSession = Depends(get_db)):
    """获取指定设备类型的可用固件版本"""
    query = select(Firmware).where(
        Firmware.deleted_at.is_(None)
    ).order_by(Firmware.created_at.desc())

    result = await db.execute(query)
    firmwares = result.scalars().all()

    return [
        {
            "id": f.id,
            "name": f.name,
            "version": f.version,
            "applicable_version": f.applicable_version,
            "force_upgrade": f.force_upgrade
        }
        for f in firmwares
    ]
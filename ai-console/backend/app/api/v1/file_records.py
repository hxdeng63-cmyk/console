from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models import File
from app.schemas import (
    FileRecordCreate, FileRecordUpdate, FileRecordResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/file-records", tags=["文件记录管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


@router.get("", response_model=PaginatedResponse)
async def list_file_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    device_id: Optional[int] = None,
    file_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取文件记录列表
    - keyword: 搜索文件名
    - device_id: 设备ID筛选
    - file_type: 文件类型筛选
    - start_date/end_date: 日期范围筛选
    """
    query = select(File)
    query = soft_delete_query(query, File)

    if keyword:
        query = query.where(File.file_name.ilike(f"%{keyword}%"))

    if device_id is not None:
        query = query.where(File.device_id == device_id)

    if file_type:
        query = query.where(File.file_type == file_type)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(File.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return PaginatedResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=[FileRecordResponse.model_validate(item) for item in items]
    )


@router.get("/tree", response_model=list)
async def get_file_tree(db: AsyncSession = Depends(get_db)):
    """Return file records grouped by org -> region -> file as a tree."""
    from app.models.device import Device
    from app.models.region import Region
    from app.models.organization import Organization

    query = (
        select(File, Device, Region, Organization)
        .outerjoin(Device, File.device_id == Device.id)
        .outerjoin(Region, Device.region_id == Region.id)
        .outerjoin(Organization, Device.org_id == Organization.id)
        .where(File.deleted_at.is_(None))
        .order_by(File.created_at.desc())
    )
    result = await db.execute(query)
    rows = result.all()

    org_map: dict = {}
    for file_record, device, region, org in rows:
        org_name = org.name if org else "未知公司"
        region_name = region.name if region else "未知区域"

        if org_name not in org_map:
            org_map[org_name] = {}
        if region_name not in org_map[org_name]:
            org_map[org_name][region_name] = []

        org_map[org_name][region_name].append({
            "id": file_record.id,
            "name": file_record.file_name,
            "isFile": True,
            "fileType": file_record.file_type or "视频",
            "eventType": file_record.file_type or "",
            "previewUrl": file_record.url or "",
            "filePath": file_record.storage_path or "",
        })

    tree = []
    org_idx = 0
    for org_name, regions in org_map.items():
        org_node = {
            "id": f"org-{org_idx}",
            "name": org_name,
            "isCompany": True,
            "children": [],
        }
        region_idx = 0
        for region_name, files in regions.items():
            region_node = {
                "id": f"org-{org_idx}-region-{region_idx}",
                "name": region_name,
                "isRegion": True,
                "children": files,
            }
            org_node["children"].append(region_node)
            region_idx += 1
        tree.append(org_node)
        org_idx += 1

    return tree


@router.get("/{file_id}", response_model=FileRecordResponse)
async def get_file_record(file_id: int, db: AsyncSession = Depends(get_db)):
    query = select(File).where(
        File.id == file_id,
        File.deleted_at.is_(None)
    )
    result = await db.execute(query)
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")
    return file_record


@router.post("", response_model=FileRecordResponse)
async def create_file_record(data: FileRecordCreate, db: AsyncSession = Depends(get_db)):
    file_record = File(**data.model_dump())
    db.add(file_record)
    await db.commit()
    await db.refresh(file_record)
    return file_record


@router.put("/{file_id}", response_model=FileRecordResponse)
async def update_file_record(
    file_id: int,
    data: FileRecordUpdate,
    db: AsyncSession = Depends(get_db)
):
    query = select(File).where(
        File.id == file_id,
        File.deleted_at.is_(None)
    )
    result = await db.execute(query)
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(file_record, key, value)

    await db.commit()
    await db.refresh(file_record)
    return file_record


@router.delete("/{file_id}")
async def delete_file_record(file_id: int, db: AsyncSession = Depends(get_db)):
    query = select(File).where(
        File.id == file_id,
        File.deleted_at.is_(None)
    )
    result = await db.execute(query)
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")

    file_record.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "删除成功"}


@router.post("/{file_id}/download")
async def download_file(file_id: int, db: AsyncSession = Depends(get_db)):
    """获取文件下载URL"""
    query = select(File).where(
        File.id == file_id,
        File.deleted_at.is_(None)
    )
    result = await db.execute(query)
    file_record = result.scalar_one_or_none()
    if not file_record:
        raise HTTPException(status_code=404, detail="文件不存在")

    return {"url": file_record.url, "file_name": file_record.file_name}
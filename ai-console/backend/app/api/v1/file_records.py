from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.media import ensure_valid_media_url
from app.models import File
from app.schemas import (
    FileRecordCreate, FileRecordUpdate, FileRecordResponse,
    PaginatedResponse
)

router = APIRouter(prefix="/file-records", tags=["文件记录管理"])


def soft_delete_query(query, model):
    return query.where(model.deleted_at.is_(None))


def _validate_source_type(source_type: Optional[str]) -> None:
    if not source_type:
        return
    from app.models.file import FileSourceType
    valid = {e.value for e in FileSourceType}
    if source_type not in valid:
        raise HTTPException(
            status_code=422,
            detail=f"source_type must be one of {valid}"
        )


@router.get("", response_model=PaginatedResponse)
async def list_file_records(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    keyword: Optional[str] = None,
    device_id: Optional[int] = None,
    file_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    event_type_id: Optional[int] = None,
    region_id: Optional[int] = None,
    org_id: Optional[int] = None,
    source_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取文件记录列表
    - keyword: 搜索文件名
    - device_id: 设备ID筛选
    - file_type: 文件类型筛选
    - start_date/end_date: 日期范围筛选
    - event_type_id: 事件类型ID筛选
    - region_id: 区域ID筛选
    - org_id: 组织ID筛选
    - source_type: 来源类型筛选（warning_event_image / warning_event_video）
    """
    from app.models.warning_event import WarningEvent

    query = select(File)
    query = soft_delete_query(query, File)

    if keyword:
        query = query.where(File.file_name.ilike(f"%{keyword}%"))

    if device_id is not None:
        query = query.where(File.device_id == device_id)

    if file_type:
        query = query.where(File.file_type == file_type)

    _validate_source_type(source_type)
    if source_type:
        query = query.where(File.source_type == source_type)

    if event_type_id is not None or region_id is not None or org_id is not None:
        query = query.outerjoin(WarningEvent, File.warning_event_id == WarningEvent.id)

    if event_type_id is not None:
        query = query.where(WarningEvent.event_type_id == event_type_id)

    if region_id is not None:
        query = query.where(WarningEvent.region_id == region_id)

    if org_id is not None:
        query = query.where(WarningEvent.org_id == org_id)

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
async def get_file_tree(
    source_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Return file records grouped by org -> region (parent-child tree) -> event type -> file.

    先加载所有 Org / Region 构建完整区域父子树（与 /device-groups/tree 同构），
    再把 file 挂到对应叶子 region 下；空 region 也会显示（与 events 页面行为一致）。
    """
    from collections import defaultdict
    from app.models.device import Device
    from app.models.region import Region
    from app.models.organization import Organization
    from app.models.warning_event import WarningEvent
    from app.models.event_type import EventType

    _validate_source_type(source_type)

    # 1. 加载所有公司（level=1）
    org_query = select(Organization).where(
        Organization.level == 1,
        Organization.deleted_at.is_(None)
    ).order_by(Organization.sort)
    orgs = (await db.execute(org_query)).scalars().all()

    # 2. 加载所有区域
    region_query = select(Region).where(Region.deleted_at.is_(None)).order_by(Region.sort)
    all_regions = (await db.execute(region_query)).scalars().all()

    # 3. 按 parent_id 构建区域树
    region_map: dict = {}
    for r in all_regions:
        region_map[r.id] = {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "level": r.level,
            "org_id": r.org_id,
            "isRegion": True,
            "children": [],
        }
    region_roots: list = []
    for r in all_regions:
        node = region_map[r.id]
        if r.parent_id and r.parent_id in region_map:
            region_map[r.parent_id]["children"].append(node)
        else:
            region_roots.append(node)

    # 4. JOIN file records（保留原 query 结构）
    query = (
        select(File, Device, Region, Organization, WarningEvent, EventType)
        .outerjoin(Device, File.device_id == Device.id)
        .outerjoin(Region, Device.region_id == Region.id)
        .outerjoin(Organization, Device.org_id == Organization.id)
        .outerjoin(WarningEvent, File.warning_event_id == WarningEvent.id)
        .outerjoin(EventType, WarningEvent.event_type_id == EventType.id)
        .where(File.deleted_at.is_(None))
        .order_by(File.created_at.desc())
        .limit(2000)
    )
    if source_type:
        query = query.where(File.source_type == source_type)
    rows = (await db.execute(query)).all()

    # 5. 聚合 file：org_id -> region_id -> {event_type_name -> {folder_name -> [file nodes]}}
    #    folder_name = Path(storage_path).parent.name（per-detection 文件夹名）
    files_by_org_region: dict = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    # 退化路径：org 或 region 缺失的 file 单独聚合，按 (event_type, folder) 二元组分桶
    fallback_files: dict = defaultdict(list)

    for file_record, device, region, org, warning_event, event_type in rows:
        event_type_name = event_type.name if event_type else "未知事件类型"
        folder_name = (
            Path(file_record.storage_path).parent.name
            if file_record.storage_path
            else "未分组"
        )
        # 归一化 fileType 为前端期望的中文：image/None → 图片；video → 视频
        _raw_type = (file_record.file_type or "").lower()
        _display_type = "图片" if _raw_type in ("image", "图片") else "视频"
        file_node = {
            "id": file_record.id,
            "name": file_record.file_name,
            "isFile": True,
            "fileType": _display_type,
            "eventType": event_type_name,
            "previewUrl": ensure_valid_media_url(file_record.url) or "",
            "filePath": ensure_valid_media_url(file_record.storage_path) or "",
        }
        if org and region:
            files_by_org_region[org.id][region.id][event_type_name][folder_name].append(file_node)
        else:
            fallback_files[(event_type_name, folder_name)].append(file_node)

    # 6. 递归 attach files 到叶子 region
    def attach_files(region_node: dict, region_files: dict) -> None:
        if not region_node.get("children"):  # 叶子
            etype_files = region_files.get(region_node["id"], {})
            for etype_name, folder_files in etype_files.items():
                if not folder_files:
                    continue
                etype_node = {
                    "id": f"region-{region_node['id']}-etype-{etype_name}",
                    "name": etype_name,
                    "isEventType": True,
                    "children": [],
                }
                for folder_name, files in folder_files.items():
                    etype_node["children"].append({
                        "id": f"region-{region_node['id']}-etype-{etype_name}-folder-{folder_name}",
                        "name": folder_name,
                        "isFolder": True,
                        "children": files,
                    })
                region_node["children"].append(etype_node)
        else:
            for child in region_node["children"]:
                attach_files(child, region_files)

    # 7. 组装最终树
    result: list = []
    for org in orgs:
        org_node = {
            "id": f"org-{org.id}",
            "name": org.name,
            "isCompany": True,
            "children": [],
        }
        org_files = files_by_org_region.get(org.id, {})
        # 把该公司下所有 region roots 挂到 org_node
        for root in region_roots:
            if root.get("org_id") == org.id:
                attach_files(root, org_files)
                org_node["children"].append(root)
        result.append(org_node)

    # 退化路径：存在 file 但 org/region 缺失（无主），聚合到 "未知公司" 节点
    if fallback_files:
        unknown_node = {
            "id": "org-unknown",
            "name": "未知公司",
            "isCompany": True,
            "children": [],
        }
        unknown_region_node = {
            "id": "region-unknown",
            "name": "未知区域",
            "isRegion": True,
            "children": [],
        }
        for (etype_name, folder_name), files in fallback_files.items():
            if not files:
                continue
            # 找或创建对应的 etype 节点
            etype_node = next(
                (c for c in unknown_region_node["children"]
                 if c.get("name") == etype_name and c.get("isEventType")),
                None,
            )
            if etype_node is None:
                etype_node = {
                    "id": f"region-unknown-etype-{etype_name}",
                    "name": etype_name,
                    "isEventType": True,
                    "children": [],
                }
                unknown_region_node["children"].append(etype_node)
            etype_node["children"].append({
                "id": f"region-unknown-etype-{etype_name}-folder-{folder_name}",
                "name": folder_name,
                "isFolder": True,
                "children": files,
            })
        if unknown_region_node["children"]:
            unknown_node["children"].append(unknown_region_node)
            result.append(unknown_node)

    return result


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
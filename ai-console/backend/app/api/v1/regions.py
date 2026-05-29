from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.region import Region
from app.models.organization import Organization
from app.models.device import Device
from app.schemas.request.region import RegionRequest, RegionResponse, RegionTreeResponse

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("", response_model=dict)
async def list_regions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    parent_id: int = Query(None),
    org_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Region).where(Region.deleted_at.is_(None))

    if keyword:
        query = query.where(Region.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(Region.parent_id == parent_id)
    if org_id is not None:
        query = query.where(Region.org_id == org_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [RegionResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/tree", response_model=list[RegionTreeResponse])
async def get_region_tree(
    org_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Region).where(Region.deleted_at.is_(None)).order_by(Region.sort)
    if org_id is not None:
        query = query.where(Region.org_id == org_id)

    result = await db.execute(query)
    all_regions = result.scalars().all()

    region_map = {r.id: RegionTreeResponse.model_validate(r) for r in all_regions}
    roots = []

    for region in all_regions:
        node = region_map[region.id]
        if region.parent_id and region.parent_id in region_map:
            region_map[region.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/full-tree", response_model=list)
async def get_full_region_tree(db: AsyncSession = Depends(get_db)):
    """返回公司-区域合并树，公司节点来自 Organization(level=1)，区域节点来自 Region"""
    # 查询所有公司级组织
    org_query = select(Organization).where(
        Organization.level == 1,
        Organization.deleted_at.is_(None)
    ).order_by(Organization.sort)
    org_result = await db.execute(org_query)
    orgs = org_result.scalars().all()

    # 查询所有区域
    region_query = select(Region).where(Region.deleted_at.is_(None)).order_by(Region.sort)
    region_result = await db.execute(region_query)
    all_regions = region_result.scalars().all()

    # 统计每个区域的设备数量
    device_count_query = (
        select(Region.id, func.count().label("count"))
        .join(Device, Device.region_id == Region.id)
        .where(Device.deleted_at.is_(None))
        .group_by(Region.id)
    )
    device_count_result = await db.execute(device_count_query)
    device_counts = {row.id: row.count for row in device_count_result.all()}

    # 构建区域映射
    region_map = {}
    for r in all_regions:
        node = {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "parent_id": r.parent_id,
            "org_id": r.org_id,
            "level": r.level,
            "sort": r.sort,
            "remark": r.remark,
            "isRegion": True,
            "device_count": device_counts.get(r.id, 0),
            "children": [],
        }
        region_map[r.id] = node

    # 构建区域树（按 parent_id 挂载）
    region_roots = []
    for r in all_regions:
        node = region_map[r.id]
        if r.parent_id and r.parent_id in region_map:
            region_map[r.parent_id]["children"].append(node)
        else:
            region_roots.append(node)

    # 递归计算每个区域的设备数量（包含所有子区域）
    def calc_device_count(node):
        total = node["device_count"]
        for child in node["children"]:
            total += calc_device_count(child)
        node["device_count"] = total
        return total

    for root in region_roots:
        calc_device_count(root)

    # 将一级区域按 org_id 分组
    org_region_map = {}
    for root in region_roots:
        org_id = root.get("org_id")
        if org_id:
            if org_id not in org_region_map:
                org_region_map[org_id] = []
            org_region_map[org_id].append(root)

    # 构建合并树
    full_tree = []
    for org in orgs:
        org_node = {
            "id": org.id,
            "name": org.name,
            "code": org.code,
            "level": org.level,
            "sort": org.sort,
            "remark": org.remark,
            "isCompany": True,
            "children": org_region_map.get(org.id, []),
        }
        full_tree.append(org_node)

    return full_tree


@router.get("/{item_id}", response_model=RegionResponse)
async def get_region(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Region).where(Region.id == item_id, Region.deleted_at.is_(None))
    result = await db.execute(query)
    region = result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")
    return RegionResponse.model_validate(region)


@router.post("", response_model=RegionResponse)
async def create_region(data: RegionRequest, db: AsyncSession = Depends(get_db)):
    dump = data.model_dump()

    # 自动计算 level
    if dump.get("parent_id"):
        # 校验父区域层级
        parent_query = select(Region).where(
            Region.id == dump["parent_id"],
            Region.deleted_at.is_(None),
        )
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent region not found")
        if parent.level >= 2:
            raise HTTPException(status_code=400, detail="Maximum 2 levels allowed")
        dump["level"] = parent.level + 1
    else:
        dump["level"] = 1
        # 一级区域必须绑定公司
        if not dump.get("org_id"):
            raise HTTPException(status_code=400, detail="org_id is required for top-level region")

    region = Region(**dump)
    db.add(region)
    await db.commit()
    await db.refresh(region)
    return RegionResponse.model_validate(region)


@router.put("/{item_id}", response_model=RegionResponse)
async def update_region(item_id: int, data: RegionRequest, db: AsyncSession = Depends(get_db)):
    query = select(Region).where(Region.id == item_id, Region.deleted_at.is_(None))
    result = await db.execute(query)
    region = result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    dump = data.model_dump()

    # 如果 parent_id 变更，重新计算 level
    new_parent_id = dump.get("parent_id")
    if new_parent_id is not None and new_parent_id != region.parent_id:
        parent_query = select(Region).where(
            Region.id == new_parent_id,
            Region.deleted_at.is_(None),
        )
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if not parent:
            raise HTTPException(status_code=400, detail="Parent region not found")
        if parent.level >= 2:
            raise HTTPException(status_code=400, detail="Maximum 2 levels allowed")
        dump["level"] = parent.level + 1
    elif new_parent_id is None and region.parent_id is not None:
        # 从子区域变为一级区域
        dump["level"] = 1
        if not dump.get("org_id") and not region.org_id:
            raise HTTPException(status_code=400, detail="org_id is required for top-level region")

    for key, value in dump.items():
        setattr(region, key, value)

    await db.commit()
    await db.refresh(region)
    return RegionResponse.model_validate(region)


@router.delete("/{item_id}")
async def delete_region(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Region).where(Region.id == item_id, Region.deleted_at.is_(None))
    result = await db.execute(query)
    region = result.scalar_one_or_none()
    if not region:
        raise HTTPException(status_code=404, detail="Region not found")

    # 检查是否有子区域
    children_query = select(Region).where(
        Region.parent_id == item_id,
        Region.deleted_at.is_(None),
    )
    children_result = await db.execute(children_query)
    children = children_result.scalars().all()
    if children:
        raise HTTPException(status_code=400, detail="Cannot delete region with children")

    region.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Region deleted"}

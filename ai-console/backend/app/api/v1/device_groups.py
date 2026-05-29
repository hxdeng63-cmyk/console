from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.device_group import DeviceGroup
from app.models.device import Device
from app.models.region import Region
from app.models.organization import Organization
from app.schemas.request.device import DeviceGroupRequest, DeviceGroupResponse

router = APIRouter(prefix="/device-groups", tags=["device-groups"])


@router.get("", response_model=dict)
async def list_device_groups(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    region_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(DeviceGroup).where(DeviceGroup.deleted_at.is_(None))

    if keyword:
        query = query.where(DeviceGroup.name.ilike(f"%{keyword}%"))
    if region_id is not None:
        query = query.where(DeviceGroup.region_id == region_id)

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


@router.get("/tree", response_model=list)
async def get_device_group_tree(db: AsyncSession = Depends(get_db)):
    """返回四层树：公司 → 大区域 → 小区域 → 设备"""
    # 查询所有公司
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

    # 查询所有设备
    device_query = select(Device).where(Device.deleted_at.is_(None))
    device_result = await db.execute(device_query)
    all_devices = device_result.scalars().all()

    # 按 region_id 分组设备
    devices_by_region: dict[int, list] = {}
    for d in all_devices:
        if d.region_id:
            devices_by_region.setdefault(d.region_id, []).append({
                "id": d.id,
                "name": d.name,
                "status": d.status,
                "device_code": d.device_code,
                "remark": d.remark,
                "org_id": d.org_id,
                "region_id": d.region_id,
                "level": "device",
            })

    # 构建区域节点映射
    region_map = {}
    for r in all_regions:
        region_map[r.id] = {
            "id": r.id,
            "name": r.name,
            "code": r.code,
            "level": r.level,
            "org_id": r.org_id,
            "parent_id": r.parent_id,
            "remark": r.remark,
            "isRegion": True,
            "device_count": len(devices_by_region.get(r.id, [])),
            "children": [],
        }

    # 按 parent_id 构建区域树
    region_roots = []
    for r in all_regions:
        node = region_map[r.id]
        if r.parent_id and r.parent_id in region_map:
            region_map[r.parent_id]["children"].append(node)
        else:
            region_roots.append(node)

    # 递归计算设备数量（包含子区域）
    def calc_device_count(node):
        total = node.get("device_count", 0)
        for child in node.get("children", []):
            total += calc_device_count(child)
        node["device_count"] = total
        return total

    for root in region_roots:
        calc_device_count(root)

    # 将设备挂到叶子区域节点
    def attach_devices(node):
        if not node.get("children"):
            node["children"] = devices_by_region.get(node["id"], [])
        else:
            for child in node["children"]:
                attach_devices(child)

    for root in region_roots:
        attach_devices(root)

    # 组装公司层
    result = []
    for org in orgs:
        org_node = {
            "id": org.id,
            "name": org.name,
            "level": "company",
            "isCompany": True,
            "device_count": 0,
            "children": [],
        }
        for region_root in region_roots:
            if region_root.get("org_id") == org.id:
                org_node["children"].append(region_root)
                org_node["device_count"] += region_root.get("device_count", 0)
        result.append(org_node)

    return result


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
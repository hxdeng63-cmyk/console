from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.region import Region
from app.schemas.request.region import RegionRequest, RegionResponse, RegionTreeResponse

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("", response_model=dict)
async def list_regions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    parent_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Region).where(Region.deleted_at.is_(None))

    if keyword:
        query = query.where(Region.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(Region.parent_id == parent_id)

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
async def get_region_tree(db: AsyncSession = Depends(get_db)):
    query = select(Region).where(Region.deleted_at.is_(None)).order_by(Region.sort)
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
    region = Region(**data.model_dump())
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

    for key, value in data.model_dump().items():
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

    region.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Region deleted"}
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.organization import Organization
from app.schemas.request.user import OrganizationRequest, OrganizationResponse, OrganizationTreeResponse

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=dict)
async def list_organizations(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    parent_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Organization).where(Organization.deleted_at.is_(None))

    if keyword:
        query = query.where(Organization.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(Organization.parent_id == parent_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [OrganizationResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/tree", response_model=list[OrganizationTreeResponse])
async def get_organization_tree(db: AsyncSession = Depends(get_db)):
    query = select(Organization).where(Organization.deleted_at.is_(None)).order_by(Organization.sort)
    result = await db.execute(query)
    all_orgs = result.scalars().all()

    def build_node(org):
        node = OrganizationTreeResponse.model_validate(org)
        node.label = org.name
        node.sortOrder = org.sort
        node.enabled = True
        return node

    org_map = {org.id: build_node(org) for org in all_orgs}
    roots = []

    for org in all_orgs:
        node = org_map[org.id]
        if org.parent_id and org.parent_id in org_map:
            org_map[org.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/{item_id}", response_model=OrganizationResponse)
async def get_organization(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Organization).where(Organization.id == item_id, Organization.deleted_at.is_(None))
    result = await db.execute(query)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse.model_validate(org)


def _map_org_fields(data: dict) -> dict:
    """Map frontend field names to backend model fields."""
    mapped = {}
    # Prefer frontend fields if present
    if data.get("label") is not None:
        mapped["name"] = data["label"]
    elif data.get("name") is not None:
        mapped["name"] = data["name"]

    if data.get("sortOrder") is not None:
        mapped["sort"] = data["sortOrder"]
    elif data.get("sort") is not None:
        mapped["sort"] = data["sort"]

    if data.get("parentId") is not None:
        mapped["parent_id"] = data["parentId"]
    elif data.get("parent_id") is not None:
        mapped["parent_id"] = data["parent_id"]

    # Pass through other fields (exclude level — backend calculates it)
    for key in ("code", "remark"):
        if key in data and data[key] is not None:
            mapped[key] = data[key]
    return mapped


@router.post("", response_model=OrganizationResponse)
async def create_organization(data: OrganizationRequest, db: AsyncSession = Depends(get_db)):
    payload = _map_org_fields(data.model_dump())

    # Auto-calculate level for child nodes
    parent_id = payload.get("parent_id")
    if parent_id is not None:
        parent_query = select(Organization).where(Organization.id == parent_id, Organization.deleted_at.is_(None))
        parent_result = await db.execute(parent_query)
        parent = parent_result.scalar_one_or_none()
        if parent:
            payload["level"] = parent.level + 1
        else:
            raise HTTPException(status_code=400, detail="Parent organization not found")
    else:
        payload["level"] = 1

    # Ensure name is present
    if not payload.get("name"):
        raise HTTPException(status_code=422, detail="Organization name is required")

    org = Organization(**payload)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return OrganizationResponse.model_validate(org)


@router.put("/{item_id}", response_model=OrganizationResponse)
async def update_organization(item_id: int, data: OrganizationRequest, db: AsyncSession = Depends(get_db)):
    query = select(Organization).where(Organization.id == item_id, Organization.deleted_at.is_(None))
    result = await db.execute(query)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    payload = _map_org_fields(data.model_dump())

    # Recalculate level if parent_id changed
    if "parent_id" in payload:
        parent_id = payload["parent_id"]
        if parent_id is not None:
            parent_query = select(Organization).where(Organization.id == parent_id, Organization.deleted_at.is_(None))
            parent_result = await db.execute(parent_query)
            parent = parent_result.scalar_one_or_none()
            if parent:
                payload["level"] = parent.level + 1
            else:
                raise HTTPException(status_code=400, detail="Parent organization not found")
        else:
            payload["level"] = 1

    for key, value in payload.items():
        setattr(org, key, value)

    await db.commit()
    await db.refresh(org)
    return OrganizationResponse.model_validate(org)


@router.delete("/{item_id}")
async def delete_organization(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Organization).where(Organization.id == item_id, Organization.deleted_at.is_(None))
    result = await db.execute(query)
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    org.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Organization deleted"}
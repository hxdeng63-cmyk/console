from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.role import Role
from app.schemas.request.user import RoleRequest, RoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=dict)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Role).where(Role.deleted_at.is_(None))

    if keyword:
        query = query.where(Role.name.ilike(f"%{keyword}%"))
    if status:
        query = query.where(Role.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [RoleResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=RoleResponse)
async def get_role(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Role).where(Role.id == item_id, Role.deleted_at.is_(None))
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return RoleResponse.model_validate(role)


@router.post("", response_model=RoleResponse)
async def create_role(data: RoleRequest, db: AsyncSession = Depends(get_db)):
    role = Role(**data.model_dump())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


@router.put("/{item_id}", response_model=RoleResponse)
async def update_role(item_id: int, data: RoleRequest, db: AsyncSession = Depends(get_db)):
    query = select(Role).where(Role.id == item_id, Role.deleted_at.is_(None))
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    for key, value in data.model_dump().items():
        setattr(role, key, value)

    await db.commit()
    await db.refresh(role)
    return RoleResponse.model_validate(role)


@router.delete("/{item_id}")
async def delete_role(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Role).where(Role.id == item_id, Role.deleted_at.is_(None))
    result = await db.execute(query)
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    role.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Role deleted"}
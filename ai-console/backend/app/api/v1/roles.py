from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.role import Role
from app.models.user import User
from app.models.user_role import UserRole
from app.models.role_menu import RoleMenu
from app.models.role_resource import RoleResource
from app.models.menu import Menu
from app.models.resource import Resource
from app.models.organization import Organization
from app.schemas.request.user import RoleRequest, RoleResponse

router = APIRouter(prefix="/roles", tags=["roles"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _role_to_dict(role: Role, usage_count: int = 0) -> dict:
    """Serialize a Role with computed frontend fields."""
    d = RoleResponse.model_validate(role).model_dump()
    d["usage_count"] = usage_count
    # camelCase aliases for frontend compatibility
    d["usageCount"] = usage_count
    d["inUse"] = d.get("in_use", False)
    d["definition"] = d.get("definition", "")
    return d


# ---------------------------------------------------------------------------
# CRUD
# ---------------------------------------------------------------------------


@router.get("", response_model=dict)
async def list_roles(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    status: str = Query(None),
    org_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    # Subquery for usage count per role (matched by User.role string field)
    if org_id:
        # Get all descendant org ids (including the company itself)
        org_ids_result = await db.execute(
            text("""
                WITH RECURSIVE org_tree AS (
                    SELECT id FROM organization WHERE id = :org_id
                    UNION ALL
                    SELECT o.id FROM organization o
                    JOIN org_tree ot ON o.parent_id = ot.id
                )
                SELECT id FROM org_tree
            """).bindparams(org_id=org_id)
        )
        org_ids = [r[0] for r in org_ids_result.all()]
        usage_subq = (
            select(User.role.label("role_code"), func.count(User.id).label("usage_count"))
            .where(User.deleted_at.is_(None), User.org_id.in_(org_ids))
            .group_by(User.role)
            .subquery()
        )
    else:
        usage_subq = (
            select(User.role.label("role_code"), func.count(User.id).label("usage_count"))
            .where(User.deleted_at.is_(None))
            .group_by(User.role)
            .subquery()
        )

    query = (
        select(Role, func.coalesce(usage_subq.c.usage_count, 0))
        .outerjoin(usage_subq, Role.code == usage_subq.c.role_code)
        .where(Role.deleted_at.is_(None))
    )

    if keyword:
        query = query.where(Role.name.ilike(f"%{keyword}%"))
    if status:
        query = query.where(Role.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    items = []
    for role, usage_count in result.all():
        items.append(_role_to_dict(role, int(usage_count)))

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{item_id}", response_model=dict)
async def get_role(item_id: int, db: AsyncSession = Depends(get_db)):
    # Fetch role
    role_result = await db.execute(
        select(Role).where(Role.id == item_id, Role.deleted_at.is_(None))
    )
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Fetch usage count (matched by User.role string field)
    usage_result = await db.execute(
        select(func.count(User.id)).where(User.role == role.code, User.deleted_at.is_(None))
    )
    usage_count = usage_result.scalar() or 0

    return _role_to_dict(role, int(usage_count))


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


# ---------------------------------------------------------------------------
# Role ↔ Users
# ---------------------------------------------------------------------------


@router.get("/{item_id}/users")
async def get_role_users(
    item_id: int,
    org_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Return all users whose User.role matches this role's code."""
    # Fetch role code first
    role_result = await db.execute(
        select(Role).where(Role.id == item_id, Role.deleted_at.is_(None))
    )
    role = role_result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    query = (
        select(User, Organization.name.label("org_name"))
        .outerjoin(Organization, Organization.id == User.org_id)
        .where(
            User.role == role.code,
            User.deleted_at.is_(None),
        )
    )

    if org_id:
        # Filter to users within the selected company (and its descendants)
        org_ids_result = await db.execute(
            text("""
                WITH RECURSIVE org_tree AS (
                    SELECT id FROM organization WHERE id = :org_id
                    UNION ALL
                    SELECT o.id FROM organization o
                    JOIN org_tree ot ON o.parent_id = ot.id
                )
                SELECT id FROM org_tree
            """).bindparams(org_id=org_id)
        )
        org_ids = [r[0] for r in org_ids_result.all()]
        query = query.where(User.org_id.in_(org_ids))

    result = await db.execute(query)

    users = []
    for user, org_name in result.all():
        # Show department name directly (not root company)
        users.append({
            "id": user.id,
            "username": user.username,
            "name": user.real_name or user.username,
            "phone": user.phone or "-",
            "org": org_name or "-",
        })
    return users


# ---------------------------------------------------------------------------
# Role ↔ Menus
# ---------------------------------------------------------------------------


@router.get("/{item_id}/menus")
async def get_role_menus(item_id: int, db: AsyncSession = Depends(get_db)):
    """Return menu tree + checked menu ids for this role."""
    # All menus
    menus_result = await db.execute(
        select(Menu).where(Menu.deleted_at.is_(None)).order_by(Menu.sort)
    )
    menus = menus_result.scalars().all()

    # Selected menu ids for this role
    selected_result = await db.execute(
        select(RoleMenu.menu_id).where(RoleMenu.role_id == item_id)
    )
    selected_ids = {r[0] for r in selected_result.all()}

    # Build tree
    def build_tree(parent_id=None):
        nodes = []
        for m in menus:
            if m.parent_id == parent_id:
                node = {
                    "id": m.id,
                    "label": m.title or m.name,
                    "children": build_tree(m.id),
                }
                nodes.append(node)
        return nodes

    return {
        "tree": build_tree(),
        "checked_ids": list(selected_ids),
    }


@router.put("/{item_id}/menus")
async def set_role_menus(
    item_id: int,
    menu_ids: list[int],
    db: AsyncSession = Depends(get_db),
):
    """Overwrite menu permissions for this role."""
    await db.execute(delete(RoleMenu).where(RoleMenu.role_id == item_id))
    for menu_id in menu_ids:
        db.add(RoleMenu(role_id=item_id, menu_id=menu_id))
    await db.commit()
    return {"message": "Role menus updated"}


# ---------------------------------------------------------------------------
# Role ↔ Resources
# ---------------------------------------------------------------------------


@router.get("/{item_id}/resources")
async def get_role_resources(item_id: int, db: AsyncSession = Depends(get_db)):
    """Return all resources + checked resource ids for this role."""
    # All resources
    resources_result = await db.execute(
        select(Resource).where(Resource.deleted_at.is_(None)).order_by(Resource.id)
    )
    resources = resources_result.scalars().all()

    # Selected resource ids for this role
    selected_result = await db.execute(
        select(RoleResource.resource_id).where(RoleResource.role_id == item_id)
    )
    selected_ids = {r[0] for r in selected_result.all()}

    return {
        "resources": [
            {
                "id": r.id,
                "name": r.resource,
                "group": r.resource_group,
                "method": r.method,
            }
            for r in resources
        ],
        "checked_ids": list(selected_ids),
    }


@router.put("/{item_id}/resources")
async def set_role_resources(
    item_id: int,
    resource_ids: list[int],
    db: AsyncSession = Depends(get_db),
):
    """Overwrite resource permissions for this role."""
    await db.execute(delete(RoleResource).where(RoleResource.role_id == item_id))
    for resource_id in resource_ids:
        db.add(RoleResource(role_id=item_id, resource_id=resource_id))
    await db.commit()
    return {"message": "Role resources updated"}

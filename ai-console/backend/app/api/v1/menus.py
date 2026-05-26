from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.menu import Menu
from app.schemas.request.user import MenuRequest, MenuResponse, MenuTreeResponse

router = APIRouter(prefix="/menus", tags=["menus"])


@router.get("", response_model=dict)
async def list_menus(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query(None),
    parent_id: int = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Menu).where(Menu.deleted_at.is_(None))

    if keyword:
        query = query.where(Menu.name.ilike(f"%{keyword}%"))
    if parent_id is not None:
        query = query.where(Menu.parent_id == parent_id)

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    return {
        "items": [MenuResponse.model_validate(item) for item in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/tree", response_model=list[MenuTreeResponse])
async def get_menu_tree(db: AsyncSession = Depends(get_db)):
    query = select(Menu).where(Menu.deleted_at.is_(None)).order_by(Menu.sort)
    result = await db.execute(query)
    all_menus = result.scalars().all()

    menu_map = {m.id: MenuTreeResponse.model_validate(m) for m in all_menus}
    roots = []

    for menu in all_menus:
        node = menu_map[menu.id]
        if menu.parent_id and menu.parent_id in menu_map:
            menu_map[menu.parent_id].children.append(node)
        else:
            roots.append(node)

    return roots


@router.get("/{item_id}", response_model=MenuResponse)
async def get_menu(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Menu).where(Menu.id == item_id, Menu.deleted_at.is_(None))
    result = await db.execute(query)
    menu = result.scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")
    return MenuResponse.model_validate(menu)


@router.post("", response_model=MenuResponse)
async def create_menu(data: MenuRequest, db: AsyncSession = Depends(get_db)):
    menu = Menu(**data.model_dump())
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return MenuResponse.model_validate(menu)


@router.put("/{item_id}", response_model=MenuResponse)
async def update_menu(item_id: int, data: MenuRequest, db: AsyncSession = Depends(get_db)):
    query = select(Menu).where(Menu.id == item_id, Menu.deleted_at.is_(None))
    result = await db.execute(query)
    menu = result.scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    for key, value in data.model_dump().items():
        setattr(menu, key, value)

    await db.commit()
    await db.refresh(menu)
    return MenuResponse.model_validate(menu)


@router.delete("/{item_id}")
async def delete_menu(item_id: int, db: AsyncSession = Depends(get_db)):
    query = select(Menu).where(Menu.id == item_id, Menu.deleted_at.is_(None))
    result = await db.execute(query)
    menu = result.scalar_one_or_none()
    if not menu:
        raise HTTPException(status_code=404, detail="Menu not found")

    menu.deleted_at = datetime.utcnow()
    await db.commit()
    return {"message": "Menu deleted"}
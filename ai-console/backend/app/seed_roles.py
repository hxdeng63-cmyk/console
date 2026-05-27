"""Seed script for roles only.

Usage:
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console" python scripts/seed_roles.py
"""

import asyncio
import os

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models.role import Role


async def count_rows(session: AsyncSession, model) -> int:
    result = await session.execute(select(func.count()).select_from(model))
    return result.scalar() or 0


async def seed_roles(session: AsyncSession) -> list[int]:
    if await count_rows(session, Role):
        print("Role table already has data, skipping seed.")
        result = await session.execute(select(Role.id))
        return [r[0] for r in result.all()]

    roles = [
        Role(name="系统管理员", code="system_admin", description="系统管理员", status="active"),
        Role(name="普通管理员", code="admin", description="普通管理员", status="active"),
        Role(name="普通用户", code="user", description="普通用户", status="active"),
        Role(name="访客", code="guest", description="访客", status="active"),
    ]
    session.add_all(roles)
    await session.flush()
    role_ids = [r.id for r in roles]
    print(f"Seeded {len(roles)} roles: {role_ids}")
    return role_ids


async def main():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            await seed_roles(session)
        await session.commit()
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())

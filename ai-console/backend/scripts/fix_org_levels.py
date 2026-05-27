import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.organization import Organization


async def fix_org_levels():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Organization).where(Organization.deleted_at.is_(None))
        )
        orgs = result.scalars().all()

        org_map = {o.id: o for o in orgs}
        fixes = []

        for org in orgs:
            if org.parent_id is None:
                expected_level = 1
            else:
                parent = org_map.get(org.parent_id)
                expected_level = (parent.level + 1) if parent else 1

            if org.level != expected_level:
                fixes.append((org.id, org.name, org.level, expected_level))
                org.level = expected_level

        if fixes:
            for oid, name, old, new in fixes:
                print(f"Fix: id={oid} name={name} level={old} -> {new}")
            await db.commit()
            print(f"Fixed {len(fixes)} records.")
        else:
            print("No fixes needed.")


if __name__ == "__main__":
    asyncio.run(fix_org_levels())

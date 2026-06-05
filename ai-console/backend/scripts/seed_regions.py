import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, text

from app.core.database import AsyncSessionLocal
from app.models.organization import Organization
from app.models.region import Region
from app.models.device import Device

# 校园/园区场景的区域模板：一级区域 -> 二级区域
CAMPUS_TEMPLATE = [
    {"name": "大学城南", "children": ["南区"]},
    {"name": "大学城北", "children": ["北区"]},
]


async def seed_regions():
    async with AsyncSessionLocal() as db:
        # 查询所有公司级组织 (level=1)
        org_query = select(Organization).where(
            Organization.level == 1,
            Organization.deleted_at.is_(None)
        )
        org_result = await db.execute(org_query)
        companies = org_result.scalars().all()

        if not companies:
            print("No companies (level=1 organizations) found. Skipping seed.")
            return

        # 幂等：先清空设备的 region_id 引用，再删除区域数据
        await db.execute(text("UPDATE device SET region_id = NULL"))
        await db.execute(delete(Region))
        print("Cleared existing region data.")

        total_regions = 0

        for company in companies:
            print(f"Seeding regions for company: {company.name} (id={company.id})")

            for i, area in enumerate(CAMPUS_TEMPLATE):
                # 创建一级区域
                region = Region(
                    name=area["name"],
                    code=area["name"],
                    parent_id=None,
                    org_id=company.id,
                    level=1,
                    sort=i + 1,
                    remark=f"{area['name']}片区"
                )
                db.add(region)
                await db.flush()  # 获取 region.id
                total_regions += 1

                # 创建二级区域
                for j, child_name in enumerate(area["children"]):
                    child_region = Region(
                        name=child_name,
                        code=child_name,
                        parent_id=region.id,
                        org_id=company.id,
                        level=2,
                        sort=j + 1,
                        remark=f"{area['name']}下属区域"
                    )
                    db.add(child_region)
                    total_regions += 1

        await db.commit()
        print(f"Seeded {len(companies)} companies with {total_regions} total regions.")


if __name__ == "__main__":
    asyncio.run(seed_regions())

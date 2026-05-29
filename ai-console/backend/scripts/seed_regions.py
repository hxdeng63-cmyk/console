import asyncio
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete, text

from app.core.database import AsyncSessionLocal
from app.models.organization import Organization
from app.models.region import Region
from app.models.device import Device

# 道路编号池
ROAD_CODES = ["S201", "G213", "G6", "S104", "G109", "S202", "G0611"]


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

            # 为每个公司随机选择 3 个道路编号
            selected_roads = random.sample(ROAD_CODES, min(3, len(ROAD_CODES)))

            for i, road_code in enumerate(selected_roads):
                # 创建一级区域
                region = Region(
                    name=road_code,
                    code=road_code,
                    parent_id=None,
                    org_id=company.id,
                    level=1,
                    sort=i + 1,
                    remark=f"{road_code}沿线"
                )
                db.add(region)
                await db.flush()  # 获取 region.id
                total_regions += 1

                # 随机创建 1-3 个子区域
                num_children = random.randint(1, 3)
                for j in range(num_children):
                    # 随机桩号：K{100-900}+{100-900}
                    start_km = random.randint(100, 900)
                    end_km = random.randint(100, 900)
                    child_name = f"{road_code}-K{start_km}+{end_km}"

                    child_region = Region(
                        name=child_name,
                        code=child_name,
                        parent_id=region.id,
                        org_id=company.id,
                        level=2,
                        sort=j + 1,
                        remark=f"{road_code}路段"
                    )
                    db.add(child_region)
                    total_regions += 1

        await db.commit()
        print(f"Seeded {len(companies)} companies with {total_regions} total regions.")


if __name__ == "__main__":
    asyncio.run(seed_regions())

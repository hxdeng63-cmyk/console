import asyncio
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.models.device import Device
from app.models.region import Region


async def seed_device_regions():
    async with AsyncSessionLocal() as db:
        # 查询所有设备
        device_query = select(Device).where(Device.deleted_at.is_(None))
        device_result = await db.execute(device_query)
        devices = device_result.scalars().all()

        if not devices:
            print("No devices found. Skipping seed.")
            return

        # 查询所有区域
        region_query = select(Region).where(Region.deleted_at.is_(None))
        region_result = await db.execute(region_query)
        regions = region_result.scalars().all()

        if not regions:
            print("No regions found. Please run seed_regions.py first.")
            return

        # 按 org_id 分组区域
        org_regions = {}
        for region in regions:
            org_id = region.org_id
            if org_id not in org_regions:
                org_regions[org_id] = []
            org_regions[org_id].append(region)

        # 清空现有设备的 region_id
        for device in devices:
            device.region_id = None
        print(f"Cleared region_id for {len(devices)} devices.")

        updated_count = 0

        for device in devices:
            device_org_id = device.org_id

            # 找到属于同一 org_id 的区域
            available_regions = org_regions.get(device_org_id, [])

            if available_regions:
                # 随机分配一个区域
                assigned_region = random.choice(available_regions)
                device.region_id = assigned_region.id

                # 确保 device.org_id 与 region.org_id 一致
                if device.org_id != assigned_region.org_id:
                    device.org_id = assigned_region.org_id

                updated_count += 1
            else:
                print(f"Warning: No regions found for device {device.id} (org_id={device_org_id})")

        await db.commit()
        print(f"Assigned regions to {updated_count}/{len(devices)} devices.")


if __name__ == "__main__":
    asyncio.run(seed_device_regions())

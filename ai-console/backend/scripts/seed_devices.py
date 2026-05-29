import asyncio
import sys
import random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.models.device import Device
from app.models.organization import Organization


async def seed_devices():
    async with AsyncSessionLocal() as db:
        # Check if devices already exist
        device_count_result = await db.execute(select(func.count()).select_from(Device).where(Device.deleted_at.is_(None)))
        device_count = device_count_result.scalar()

        if device_count > 0:
            print(f"Device table has {device_count} records, skipping seed.")
            return

        # Get all organizations
        org_query = select(Organization).where(Organization.deleted_at.is_(None))
        org_result = await db.execute(org_query)
        orgs = org_result.scalars().all()

        if not orgs:
            print("No organizations found. Skipping seed.")
            return

        # Create 20 devices
        for i in range(20):
            org = random.choice(orgs)
            device = Device(
                device_code=f"DEV{1000 + i:04d}",
                name=f"设备{1000 + i}",
                status=random.choice(["active", "inactive"]),
                access_type=random.choice(["direct", "indirect"]),
                device_type=random.choice(["camera", "sensor", "gateway"]),
                longitude=random.uniform(100.0, 110.0),
                latitude=random.uniform(30.0, 40.0),
                org_id=org.id,
                region_id=None,
            )
            db.add(device)

        await db.commit()
        print(f"Inserted 20 devices.")


if __name__ == "__main__":
    asyncio.run(seed_devices())

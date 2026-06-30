"""Seed local MP4 data sources for sample devices.

Matches devices by name against files in docs/monitoring/ and updates or creates
a DataSource with access_type='本地' and rtsp_url='docs/monitoring/{device_name}.mp4'.

Run with:
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console" python scripts/seed_local_mp4.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.device import Device
from app.models.data_source import DataSource


MP4_DIR = Path(__file__).resolve().parents[3] / "docs" / "monitoring"


async def seed_local_mp4():
    async with AsyncSessionLocal() as db:
        # Find all existing MP4 files
        mp4_files = {p.stem: p for p in MP4_DIR.glob("*.mp4")}
        if not mp4_files:
            print(f"No MP4 files found in {MP4_DIR}, skipping seed.")
            return

        print(f"Found {len(mp4_files)} MP4 files: {', '.join(sorted(mp4_files))}")

        # Find devices matching MP4 filenames
        result = await db.execute(
            select(Device).where(
                Device.deleted_at.is_(None),
                Device.name.in_(list(mp4_files.keys())),
            )
        )
        devices = result.scalars().all()
        print(f"Matched {len(devices)} devices: {', '.join(d.name for d in devices)}")

        updated = 0
        created = 0
        for device in devices:
            rel_path = f"docs/monitoring/{device.name}.mp4"
            ds_result = await db.execute(
                select(DataSource).where(
                    DataSource.device_id == device.id,
                    DataSource.deleted_at.is_(None),
                )
            )
            ds = ds_result.scalar_one_or_none()
            if ds:
                ds.access_type = "本地"
                ds.rtsp_url = rel_path
                ds.name = f"{device.name}-本地视频"
                updated += 1
            else:
                ds = DataSource(
                    name=f"{device.name}-本地视频",
                    access_type="本地",
                    rtsp_url=rel_path,
                    device_id=device.id,
                    status="在线",
                )
                db.add(ds)
                created += 1

        await db.commit()
        print(f"Updated {updated} existing DataSource records.")
        print(f"Created {created} new DataSource records.")


if __name__ == "__main__":
    asyncio.run(seed_local_mp4())

"""Seed traffic algorithm and event types.

Run with:
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console" python scripts/seed_traffic_event_types.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.algorithm import Algorithm
from app.models.event_type import EventType


EVENT_TYPES = [
    ("jam", "交通阻塞", "detection", 3, "traffic_jam"),
    ("anomaly", "异常停车", "detection", 3, "vehicle_counting"),
    ("flow", "流量统计", "detection", 1, "vehicle_counting"),
    ("reverse", "逆向行驶", "detection", 3, "reverse_detection"),
    ("pedestrian", "行人闯入", "detection", 3, "pedestrian_intrusion"),
    ("accident", "疑似事故", "detection", 4, "accident_detection"),
    ("vest", "反光衣检测", "detection", 3, "vest_detection"),
]


async def seed_traffic_event_types(db: AsyncSession) -> None:
    # Ensure traffic is the single primary traffic algorithm; deprecate legacy 交通算法 duplicate.
    result = await db.execute(select(Algorithm).where(Algorithm.name == "traffic"))
    algorithm = result.scalar_one_or_none()
    if algorithm is None:
        algorithm = Algorithm(name="traffic", description="交通事件检测算法", business_category="traffic")
        db.add(algorithm)
        await db.commit()
        await db.refresh(algorithm)
        print(f"Created Algorithm traffic (id={algorithm.id})")
    else:
        print(f"Algorithm traffic already exists (id={algorithm.id})")

    # Soft-delete the legacy Chinese-name duplicate so it no longer shows in algorithm management.
    dup_result = await db.execute(
        select(Algorithm).where(Algorithm.name == "交通算法", Algorithm.deleted_at.is_(None))
    )
    duplicate = dup_result.scalar_one_or_none()
    if duplicate is not None:
        duplicate.deleted_at = datetime.utcnow()
        await db.commit()
        print(f"Soft-deleted legacy duplicate 交通算法 (id={duplicate.id})")

    existing_result = await db.execute(
        select(EventType).where(
            EventType.algorithm_id == algorithm.id,
            EventType.deleted_at.is_(None),
        )
    )
    existing_objs = existing_result.scalars().all()

    created = 0
    updated = 0
    for name, description, category, severity, module_name in EVENT_TYPES:
        existing_event = next(
            (et for et in existing_objs if et.name == name), None
        )
        if existing_event is None:
            db.add(
                EventType(
                    algorithm_id=algorithm.id,
                    name=name,
                    description=description,
                    category=category,
                    severity=severity,
                    module_name=module_name,
                )
            )
            created += 1
        else:
            if existing_event.module_name != module_name:
                existing_event.module_name = module_name
                updated += 1

    if created or updated:
        await db.commit()
        print(f"Created {created} and updated {updated} traffic event types")
    else:
        print("Traffic event types already seeded")


async def main():
    async with AsyncSessionLocal() as db:
        await seed_traffic_event_types(db)


if __name__ == "__main__":
    asyncio.run(main())

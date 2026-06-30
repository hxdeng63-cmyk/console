"""Clean up duplicate traffic algorithm.

The legacy `交通算法` record and its event types are soft-deleted; all references
are migrated to the primary `traffic` algorithm so old records stay valid.

Run with:
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console" python scripts/cleanup_traffic_algorithm_duplicate.py
"""

import asyncio
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.algorithm import Algorithm
from app.models.deployment import Deployment
from app.models.event_type import EventType
from app.models.linkage_rule import LinkageRule
from app.models.task import Task
from app.models.warning_event import WarningEvent


async def cleanup_traffic_duplicate(db: AsyncSession) -> None:
    primary_result = await db.execute(select(Algorithm).where(Algorithm.name == "traffic", Algorithm.deleted_at.is_(None)))
    primary = primary_result.scalar_one_or_none()
    if primary is None:
        raise RuntimeError("Primary 'traffic' algorithm not found. Run seed_traffic_event_types.py first.")

    dup_result = await db.execute(select(Algorithm).where(Algorithm.name == "交通算法", Algorithm.deleted_at.is_(None)))
    duplicate = dup_result.scalar_one_or_none()
    if duplicate is None:
        print("No legacy 交通算法 duplicate found. Nothing to clean up.")
        return

    dup_event_ids_result = await db.execute(
        select(EventType.id).where(EventType.algorithm_id == duplicate.id, EventType.deleted_at.is_(None))
    )
    dup_event_ids = {row[0] for row in dup_event_ids_result.all()}

    # Migrate algorithm references to primary traffic algorithm.
    for model, fk in (
        (Deployment, Deployment.algorithm_id),
        (LinkageRule, LinkageRule.algorithm_id),
        (Task, Task.algorithm_id),
        (WarningEvent, WarningEvent.algorithm_id),
    ):
        await db.execute(update(model).where(fk == duplicate.id).values({fk.name: primary.id}))

    # Old event type IDs no longer map to traffic README events; clear them to avoid dangling FKs.
    if dup_event_ids:
        await db.execute(
            update(WarningEvent)
            .where(WarningEvent.event_type_id.in_(dup_event_ids))
            .values({WarningEvent.event_type_id.name: None})
        )
        await db.execute(
            update(LinkageRule)
            .where(LinkageRule.event_type_id.in_(dup_event_ids))
            .values({LinkageRule.event_type_id.name: None})
        )
        await db.execute(
            update(EventType)
            .where(EventType.id.in_(dup_event_ids))
            .values({EventType.deleted_at.name: datetime.utcnow()})
        )

    duplicate.deleted_at = datetime.utcnow()
    await db.commit()
    print(f"Migrated references from 交通算法 (id={duplicate.id}) to traffic (id={primary.id})")
    print(f"Soft-deleted legacy algorithm and {len(dup_event_ids)} legacy event types.")


async def main():
    async with AsyncSessionLocal() as db:
        await cleanup_traffic_duplicate(db)


if __name__ == "__main__":
    asyncio.run(main())

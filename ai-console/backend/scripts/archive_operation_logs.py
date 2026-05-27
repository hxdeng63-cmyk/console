#!/usr/bin/env python3
"""Archive old operation logs by soft-deleting records older than retention days."""

import asyncio
import os
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console",
)

# Retention period: logs older than this many days are archived
RETENTION_DAYS = int(os.getenv("OPERATION_LOG_RETENTION_DAYS", "90"))

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def archive():
    async with AsyncSessionLocal() as db:
        from app.models.operation_log import OperationLog
        from sqlalchemy import func

        cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)

        # Count how many will be archived
        count_result = await db.execute(
            select(func.count())
            .select_from(OperationLog)
            .where(OperationLog.deleted_at.is_(None), OperationLog.action_time < cutoff)
        )
        to_archive = count_result.scalar() or 0

        if to_archive == 0:
            print(f"No operation logs older than {RETENTION_DAYS} days to archive.")
            return

        # Soft-delete old logs
        result = await db.execute(
            update(OperationLog)
            .where(OperationLog.deleted_at.is_(None), OperationLog.action_time < cutoff)
            .values(deleted_at=datetime.utcnow())
        )
        await db.commit()

        print(f"Archived {result.rowcount} operation logs older than {RETENTION_DAYS} days (cutoff: {cutoff.isoformat()}).")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(archive())

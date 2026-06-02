"""
将历史 warning_event 的 image_url/video_url 反向同步到 file 表。

特性：
- 批次处理（默认 batch_size=200）
- 幂等性检查：跳过已存在 file 记录的 warning_event
- 断点续传：通过 .migration_checkpoint 文件记录进度
- 错误隔离：单条记录失败不影响整个批次
- 使用 AsyncSessionLocal（代码库的 session 工厂）
"""

import asyncio
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select, insert, func, exists as sql_exists
from app.core.database import AsyncSessionLocal
from app.models import WarningEvent, File

BATCH_SIZE = 200
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), ".migration_checkpoint")


async def get_last_processed_id() -> int:
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0


async def save_checkpoint(last_id: int):
    with open(CHECKPOINT_FILE, "w") as f:
        f.write(str(last_id))


async def migrate_batch(session, min_id: int, batch_size: int) -> tuple[int, int, int, int]:
    """返回 (processed_events, created_files, skipped_events, max_id)"""
    subq = select(File.id).where(
        File.warning_event_id == WarningEvent.id
    ).exists()

    query = (
        select(WarningEvent)
        .where(WarningEvent.id > min_id)
        .where(~subq)
        .order_by(WarningEvent.id)
        .limit(batch_size)
    )
    result = await session.execute(query)
    events = result.scalars().all()

    if not events:
        return 0, 0, 0, min_id

    files_to_insert = []
    processed = 0
    skipped = 0
    max_id = min_id

    for event in events:
        processed += 1
        max_id = max(max_id, event.id)

        # 双重幂等性检查
        existing = await session.execute(
            select(func.count()).where(File.warning_event_id == event.id)
        )
        if existing.scalar() > 0:
            skipped += 1
            continue

        if event.image_url:
            files_to_insert.append({
                'warning_event_id': event.id,
                'device_id': event.device_id,
                'source_type': 'warning_event_image',
                'file_name': os.path.basename(event.image_url) or 'image.jpg',
                'file_type': 'image',
                'url': event.image_url,
                'storage_path': event.image_url,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
            })
        if event.video_url:
            files_to_insert.append({
                'warning_event_id': event.id,
                'device_id': event.device_id,
                'source_type': 'warning_event_video',
                'file_name': os.path.basename(event.video_url) or 'video.mp4',
                'file_type': 'video',
                'url': event.video_url,
                'storage_path': event.video_url,
                'created_at': datetime.now(timezone.utc),
                'updated_at': datetime.now(timezone.utc),
            })

    if files_to_insert:
        await session.execute(insert(File), files_to_insert)
        await session.commit()

    return processed, len(files_to_insert), skipped, max_id


async def main():
    last_id = await get_last_processed_id()
    total_events = 0
    total_files = 0
    total_skipped = 0

    async with AsyncSessionLocal() as session:
        while True:
            try:
                processed, files, skipped, max_id = await migrate_batch(
                    session, last_id, BATCH_SIZE
                )
                if processed == 0:
                    break
                total_events += processed
                total_files += files
                total_skipped += skipped
                last_id = max_id
                await save_checkpoint(last_id)
                print(f"Batch: processed={processed}, files={files}, skipped={skipped}, last_id={last_id}")
            except Exception as e:
                print(f"Batch failed at last_id={last_id}: {e}")
                await session.rollback()
                raise

    print(f"\nMigration complete!")
    print(f"Events: {total_events}, Files: {total_files}, Skipped: {total_skipped}")

    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)


if __name__ == "__main__":
    asyncio.run(main())

from datetime import datetime, timedelta
from typing import Literal

from sqlalchemy import update, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CleanRecord, CleanupPolicy, File, WarningEvent


async def get_or_create_policy(db: AsyncSession) -> CleanupPolicy:
    """获取全局策略配置，不存在则创建默认配置"""
    query = select(CleanupPolicy).where(CleanupPolicy.id == 1)
    result = await db.execute(query)
    policy = result.scalar_one_or_none()

    if not policy:
        policy = CleanupPolicy(
            id=1,
            alert_enabled=True,
            alert_days=90,
            video_enabled=True,
            video_days=60,
            strategy="scheduled",
            execute_time="02:00",
        )
        db.add(policy)
        await db.commit()
        await db.refresh(policy)

    return policy


async def execute_cleanup(
    db: AsyncSession,
    dimension: Literal["all", "warning_event", "video_file"] = "all",
) -> CleanRecord:
    """执行数据清理的核心逻辑"""
    policy = await get_or_create_policy(db)
    now = datetime.utcnow()

    # 创建清理记录
    clean_record = CleanRecord(
        type="cleanup",
        status="running",
        progress=0,
        dimension=dimension,
    )
    db.add(clean_record)
    await db.commit()
    await db.refresh(clean_record)

    total_cleaned = 0
    total_size = 0

    try:
        # 1. 清理预警事件
        if dimension in ("all", "warning_event") and policy.alert_enabled:
            cutoff = now - timedelta(days=policy.alert_days)
            cleaned, size = await _cleanup_warning_events(db, cutoff)
            total_cleaned += cleaned
            total_size += size

        # 2. 清理视频文件
        if dimension in ("all", "video_file") and policy.video_enabled:
            cutoff = now - timedelta(days=policy.video_days)
            cleaned, size = await _cleanup_video_files(db, cutoff)
            total_cleaned += cleaned
            total_size += size

        clean_record.status = "completed"
        clean_record.progress = 100
        clean_record.records_cleaned = total_cleaned
        clean_record.clean_size_bytes = total_size
        clean_record.cutoff_time = now

    except Exception as e:
        clean_record.status = "failed"
        clean_record.error_message = str(e)

    await db.commit()
    await db.refresh(clean_record)
    return clean_record


async def _cleanup_warning_events(db: AsyncSession, cutoff: datetime) -> tuple[int, int]:
    """软删除过期的预警事件记录，返回 (清理条数, 清理文件总字节数)"""
    # 查询需要清理的预警事件
    query = select(WarningEvent.id).where(
        WarningEvent.report_time < cutoff,
        WarningEvent.deleted_at.is_(None),
    )
    result = await db.execute(query)
    event_ids = [row[0] for row in result.all()]

    if not event_ids:
        return 0, 0

    # 统计关联文件大小
    size_result = await db.execute(
        select(File.file_size_bytes).where(
            File.warning_event_id.in_(event_ids),
            File.deleted_at.is_(None),
        )
    )
    total_size = sum(
        row[0] or 0 for row in size_result.all() if row[0] is not None
    )

    # 软删除预警事件
    await db.execute(
        update(WarningEvent)
        .where(WarningEvent.id.in_(event_ids))
        .values(deleted_at=datetime.utcnow())
    )

    # 软删除关联的 file 记录
    await db.execute(
        update(File)
        .where(File.warning_event_id.in_(event_ids), File.deleted_at.is_(None))
        .values(deleted_at=datetime.utcnow())
    )

    # 清空 video_url / image_url，避免前端继续请求已删除文件
    await db.execute(
        update(WarningEvent)
        .where(WarningEvent.id.in_(event_ids))
        .values(video_url=None, image_url=None)
    )

    return len(event_ids), total_size


async def _cleanup_video_files(db: AsyncSession, cutoff: datetime) -> tuple[int, int]:
    """软删除过期的视频文件记录，返回 (清理条数, 清理文件总字节数)"""
    # 查询需要清理的视频文件
    query = select(File.id, File.warning_event_id, File.file_size_bytes).where(
        File.created_at < cutoff,
        File.source_type == "warning_event_video",
        File.deleted_at.is_(None),
    )
    result = await db.execute(query)
    rows = result.all()

    if not rows:
        return 0, 0

    file_ids = [row[0] for row in rows]
    event_ids = list(set(row[1] for row in rows if row[1]))
    total_size = sum(row[2] or 0 for row in rows if row[2] is not None)

    # 软删除视频文件记录
    await db.execute(
        update(File)
        .where(File.id.in_(file_ids))
        .values(deleted_at=datetime.utcnow())
    )

    # 清空关联预警事件的 video_url，避免前端继续请求已删除文件
    if event_ids:
        await db.execute(
            update(WarningEvent)
            .where(WarningEvent.id.in_(event_ids))
            .values(video_url=None)
        )

    return len(file_ids), total_size

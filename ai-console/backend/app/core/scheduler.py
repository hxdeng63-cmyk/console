import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.database import AsyncSessionLocal
from app.services.cleanup_service import execute_cleanup

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_cleanup():
    """定时清理任务"""
    logger.info("[Scheduler] Starting scheduled cleanup job")
    try:
        async with AsyncSessionLocal() as db:
            from app.services.cleanup_service import get_or_create_policy
            policy = await get_or_create_policy(db)

            if policy.strategy != "scheduled":
                logger.info("[Scheduler] Cleanup strategy is not 'scheduled', skipping")
                return

            await execute_cleanup(db, dimension="all")
            logger.info("[Scheduler] Scheduled cleanup completed")
    except Exception as e:
        logger.error(f"[Scheduler] Scheduled cleanup failed: {e}")


def start_scheduler():
    """启动定时任务调度器"""
    # 每天凌晨 02:00 执行
    scheduler.add_job(
        scheduled_cleanup,
        trigger=CronTrigger(hour=2, minute=0),
        id="daily_cleanup",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[Scheduler] APScheduler started with daily cleanup at 02:00")


def shutdown_scheduler():
    """关闭定时任务调度器"""
    scheduler.shutdown()
    logger.info("[Scheduler] APScheduler shut down")

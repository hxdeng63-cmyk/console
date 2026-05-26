import asyncio
import sys
sys.path.insert(0, r"E:\python\code\console\ai-console\backend")

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.models.microservice import Microservice


async def seed_microservices():
    async with AsyncSessionLocal() as db:
        count_result = await db.execute(select(func.count()).select_from(Microservice).where(Microservice.deleted_at.is_(None)))
        count = count_result.scalar()
        if count > 0:
            print(f"Microservice table already has {count} records, skipping seed.")
            return

        now = datetime.utcnow()

        services = [
            ("001", "用户服务"),
            ("002", "菜单服务"),
            ("003", "系统设置"),
            ("004", "联动服务"),
            ("005", "算法服务"),
            ("006", "预警服务"),
            ("007", "设备接入"),
            ("008", "数据清理"),
            ("009", "监控服务"),
            ("010", "事件统计"),
            ("011", "固件服务"),
            ("012", "部署服务"),
            ("013", "数据看板"),
            ("014", "日志审计"),
            ("015", "任务调度"),
        ]

        for code, name in services:
            db.add(Microservice(
                code=code,
                name=name,
                service_name=name,
                status="active",
                created_at=now,
                updated_at=now
            ))

        await db.commit()
        print(f"Inserted {len(services)} microservices.")


if __name__ == "__main__":
    asyncio.run(seed_microservices())

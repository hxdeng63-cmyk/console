#!/usr/bin/env python3
"""Seed operation logs with simulated data."""

import asyncio
import os
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console",
)

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Sample data
USERS = ["zhangsan", "lisi", "wangwu", "zhaoliu", "sunqi", "shubao", "yaojin"]
METHODS = ["GET", "POST", "PUT", "DELETE"]
IPS = ["192.168.1.10", "192.168.1.25", "10.0.0.5", "172.16.0.8", "192.168.1.100"]

ENDPOINTS = [
    ("/api/v1/users", "GET", "查询用户列表"),
    ("/api/v1/users", "POST", "创建用户"),
    ("/api/v1/users/1", "GET", "查看用户详情"),
    ("/api/v1/users/1", "PUT", "更新用户信息"),
    ("/api/v1/users/1", "DELETE", "删除用户"),
    ("/api/v1/users/1/reset-password", "POST", "重置密码"),
    ("/api/v1/roles", "GET", "查询角色列表"),
    ("/api/v1/roles", "POST", "创建角色"),
    ("/api/v1/roles/1", "PUT", "更新角色"),
    ("/api/v1/roles/1", "DELETE", "删除角色"),
    ("/api/v1/organizations/tree", "GET", "获取组织树"),
    ("/api/v1/organizations", "POST", "创建组织"),
    ("/api/v1/devices", "GET", "查询设备列表"),
    ("/api/v1/devices", "POST", "创建设备"),
    ("/api/v1/device-groups/tree", "GET", "获取设备组树"),
    ("/api/v1/linkage-rules", "GET", "查询联动规则"),
    ("/api/v1/linkage-rules", "POST", "创建联动规则"),
    ("/api/v1/algorithms", "GET", "查询算法列表"),
    ("/api/v1/algorithms", "POST", "创建算法"),
    ("/api/v1/algorithm-events", "GET", "查询算法事件"),
    ("/api/v1/algorithm-events/export", "GET", "导出算法事件"),
    ("/api/v1/tasks", "GET", "查询任务列表"),
    ("/api/v1/tasks", "POST", "创建任务"),
    ("/api/v1/menus", "GET", "查询菜单列表"),
    ("/api/v1/resources", "GET", "查询资源列表"),
    ("/api/v1/microservices", "GET", "查询微服务列表"),
]


def random_status_code(method: str) -> int:
    weights = [0.85, 0.05, 0.05, 0.03, 0.02]
    codes = [200, 201, 400, 401, 500]
    if method == "POST":
        weights = [0.30, 0.60, 0.04, 0.03, 0.03]
    elif method == "DELETE":
        weights = [0.20, 0.70, 0.03, 0.03, 0.04]
    return random.choices(codes, weights=weights)[0]


async def seed():
    async with AsyncSessionLocal() as db:
        from app.models.operation_log import OperationLog

        # Check existing count
        from sqlalchemy import select, func
        result = await db.execute(select(func.count()).select_from(OperationLog))
        count = result.scalar()
        if count and count > 0:
            print(f"Operation log table already has {count} records. Skipping seed.")
            return

        now = datetime.utcnow()
        logs = []

        for _ in range(200):
            path, method, description = random.choice(ENDPOINTS)
            status_code = random_status_code(method)
            action_time = now - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            log = OperationLog(
                username=random.choice(USERS),
                method=method,
                path=path,
                ip=random.choice(IPS),
                status_code=status_code,
                result="success" if status_code < 400 else "failed",
                description=description,
                action_time=action_time,
            )
            logs.append(log)

        db.add_all(logs)
        await db.commit()
        print(f"Seeded {len(logs)} operation logs.")


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    asyncio.run(seed())

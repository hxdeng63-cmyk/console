import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.resource import Resource
from app.main import app


# API tag -> (service_code, service_name)
SERVICE_CODE_MAP = {
    "users": ("001", "用户服务"),
    "menus": ("002", "菜单服务"),
    "resources": ("002", "菜单服务"),
    "roles": ("001", "用户服务"),
    "organizations": ("001", "用户服务"),
    "operation-logs": ("014", "日志审计"),
    "licenses": ("003", "系统设置"),
    "ui-themes": ("003", "系统设置"),
    "popup-settings": ("003", "系统设置"),
    "video-settings": ("003", "系统设置"),
    "dispose-tags": ("003", "系统设置"),
    "linkage-rules": ("004", "联动服务"),
    "push-histories": ("004", "联动服务"),
    "tasks": ("015", "任务调度"),
    "algorithms": ("005", "算法服务"),
    "algorithm-services": ("005", "算法服务"),
    "algorithm-events": ("005", "算法服务"),
    "event-types": ("005", "算法服务"),
    "annotations": ("005", "算法服务"),
    "warning-events": ("006", "预警服务"),
    "event-stats": ("010", "事件统计"),
    "devices": ("007", "设备接入"),
    "device-groups": ("007", "设备接入"),
    "device-streams": ("007", "设备接入"),
    "regions": ("007", "设备接入"),
    "data-sources": ("007", "设备接入"),
    "access-platforms": ("007", "设备接入"),
    "clean-records": ("008", "数据清理"),
    "dashboard": ("013", "数据看板"),
    "deployments": ("012", "部署服务"),
    "deployment-schedules": ("012", "部署服务"),
    "firmwares": ("011", "固件服务"),
    "file-records": ("003", "系统设置"),
    "microservices": ("003", "系统设置"),
}


def normalize_group(tag: str) -> str:
    """将 FastAPI router tag 转为 resource_group snake_case"""
    return tag.lower().replace(" ", "_").replace("-", "_")


def tag_to_service_code(tag: str) -> str:
    """根据 tag 查找 service_code"""
    key = tag.lower().replace(" ", "-").replace("_", "-")
    code, _ = SERVICE_CODE_MAP.get(key, ("", ""))
    return code


async def seed_resources():
    async with AsyncSessionLocal() as db:
        # 幂等检查
        result = await db.execute(
            select(func.count()).select_from(Resource).where(Resource.deleted_at.is_(None))
        )
        if result.scalar() > 0:
            print("Resource table already has data, skipping seed.")
            return

        resources = []
        seen = set()

        for route in app.routes:
            if not hasattr(route, "methods"):
                continue
            path = route.path
            methods = route.methods - {"HEAD"}
            tags = getattr(route, "tags", [""])
            tag = tags[0] if tags else ""

            # 跳过系统端点
            if not path.startswith("/api/v1/"):
                continue

            group = normalize_group(tag)
            service_code = tag_to_service_code(tag)

            for method in sorted(methods):
                key = (path, method)
                if key in seen:
                    continue
                seen.add(key)

                description = f"{tag} {method}"
                resources.append(
                    Resource(
                        resource=path,
                        resource_group=group,
                        method=method,
                        service_code=service_code,
                        description=description,
                        hidden=False,
                    )
                )

        db.add_all(resources)
        await db.commit()
        print(f"Resource seed completed! Inserted {len(resources)} resources.")


if __name__ == "__main__":
    asyncio.run(seed_resources())

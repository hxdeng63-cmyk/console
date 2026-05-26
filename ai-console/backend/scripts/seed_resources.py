import asyncio
import sys
sys.path.insert(0, r"E:\python\code\console\ai-console\backend")

from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import AsyncSessionLocal
from app.models.resource import Resource


async def seed_resources():
    async with AsyncSessionLocal() as db:
        count_result = await db.execute(select(func.count()).select_from(Resource).where(Resource.deleted_at.is_(None)))
        count = count_result.scalar()
        if count > 0:
            print(f"Resource table already has {count} records, skipping seed.")
            return

        now = datetime.utcnow()

        resources = [
            # 用户服务 (001)
            ("001", "用户管理", "GET /api/v1/users", "获取用户列表", "GET", False),
            ("001", "用户管理", "POST /api/v1/users", "创建用户", "POST", False),
            ("001", "用户管理", "PUT /api/v1/users/{id}", "更新用户", "PUT", False),
            ("001", "用户管理", "DELETE /api/v1/users/{id}", "删除用户", "DELETE", False),
            ("001", "角色管理", "GET /api/v1/roles", "获取角色列表", "GET", False),
            ("001", "角色管理", "POST /api/v1/roles", "创建角色", "POST", False),
            ("001", "角色管理", "PUT /api/v1/roles/{id}", "更新角色", "PUT", False),
            ("001", "角色管理", "DELETE /api/v1/roles/{id}", "删除角色", "DELETE", False),
            ("001", "组织管理", "GET /api/v1/organizations", "获取组织列表", "GET", False),
            ("001", "组织管理", "POST /api/v1/organizations", "创建组织", "POST", False),
            ("001", "组织管理", "PUT /api/v1/organizations/{id}", "更新组织", "PUT", False),
            ("001", "组织管理", "DELETE /api/v1/organizations/{id}", "删除组织", "DELETE", False),

            # 菜单服务 (002)
            ("002", "菜单管理", "GET /api/v1/menus", "获取菜单列表", "GET", False),
            ("002", "菜单管理", "GET /api/v1/menus/tree", "获取菜单树", "GET", False),
            ("002", "菜单管理", "POST /api/v1/menus", "创建菜单", "POST", False),
            ("002", "菜单管理", "PUT /api/v1/menus/{id}", "更新菜单", "PUT", False),
            ("002", "菜单管理", "DELETE /api/v1/menus/{id}", "删除菜单", "DELETE", False),

            # 系统设置 (003)
            ("003", "系统设置", "GET /api/v1/video-settings", "获取录像设置", "GET", False),
            ("003", "系统设置", "PUT /api/v1/video-settings/{id}", "更新录像设置", "PUT", False),
            ("003", "系统设置", "GET /api/v1/popup-settings", "获取弹窗设置", "GET", False),
            ("003", "系统设置", "PUT /api/v1/popup-settings/{id}", "更新弹窗设置", "PUT", False),
            ("003", "系统设置", "GET /api/v1/dispose-tags", "获取处置标签", "GET", False),
            ("003", "系统设置", "POST /api/v1/dispose-tags", "创建处置标签", "POST", False),
            ("003", "系统设置", "PUT /api/v1/dispose-tags/{id}", "更新处置标签", "PUT", False),
            ("003", "系统设置", "DELETE /api/v1/dispose-tags/{id}", "删除处置标签", "DELETE", False),

            # 联动服务 (004)
            ("004", "联动管理", "GET /api/v1/linkage-rules", "获取联动规则", "GET", False),
            ("004", "联动管理", "POST /api/v1/linkage-rules", "创建联动规则", "POST", False),
            ("004", "联动管理", "PUT /api/v1/linkage-rules/{id}", "更新联动规则", "PUT", False),
            ("004", "联动管理", "DELETE /api/v1/linkage-rules/{id}", "删除联动规则", "DELETE", False),
            ("004", "联动管理", "GET /api/v1/push-histories", "获取推送历史", "GET", False),
            ("004", "联动管理", "DELETE /api/v1/push-histories/{id}", "删除推送历史", "DELETE", False),

            # 算法服务 (005)
            ("005", "算法管理", "GET /api/v1/algorithms", "获取算法列表", "GET", False),
            ("005", "算法管理", "POST /api/v1/algorithms", "创建算法", "POST", False),
            ("005", "算法管理", "PUT /api/v1/algorithms/{id}", "更新算法", "PUT", False),
            ("005", "算法管理", "DELETE /api/v1/algorithms/{id}", "删除算法", "DELETE", False),
            ("005", "算法管理", "GET /api/v1/algorithm-services", "获取算法服务", "GET", False),
            ("005", "算法管理", "POST /api/v1/algorithm-services", "创建算法服务", "POST", False),
            ("005", "算法管理", "PUT /api/v1/algorithm-services/{id}", "更新算法服务", "PUT", False),
            ("005", "算法管理", "DELETE /api/v1/algorithm-services/{id}", "删除算法服务", "DELETE", False),

            # 预警服务 (006)
            ("006", "预警管理", "GET /api/v1/warning-events", "获取预警事件", "GET", False),
            ("006", "预警管理", "PUT /api/v1/warning-events/{id}", "更新预警事件", "PUT", False),
            ("006", "预警管理", "DELETE /api/v1/warning-events/{id}", "删除预警事件", "DELETE", False),
            ("006", "事件统计", "GET /api/v1/event-stats", "获取事件统计", "GET", False),
            ("006", "事件统计", "GET /api/v1/event-stats/scenes", "获取场景统计", "GET", False),

            # 设备接入 (007)
            ("007", "设备管理", "GET /api/v1/devices", "获取设备列表", "GET", False),
            ("007", "设备管理", "POST /api/v1/devices", "创建设备", "POST", False),
            ("007", "设备管理", "PUT /api/v1/devices/{id}", "更新设备", "PUT", False),
            ("007", "设备管理", "DELETE /api/v1/devices/{id}", "删除设备", "DELETE", False),
            ("007", "设备管理", "GET /api/v1/device-groups", "获取设备组", "GET", False),
            ("007", "设备管理", "POST /api/v1/device-groups", "创建设备组", "POST", False),
            ("007", "设备管理", "PUT /api/v1/device-groups/{id}", "更新设备组", "PUT", False),
            ("007", "设备管理", "DELETE /api/v1/device-groups/{id}", "删除设备组", "DELETE", False),
            ("007", "区域管理", "GET /api/v1/regions", "获取区域列表", "GET", False),
            ("007", "区域管理", "POST /api/v1/regions", "创建区域", "POST", False),
            ("007", "区域管理", "PUT /api/v1/regions/{id}", "更新区域", "PUT", False),
            ("007", "区域管理", "DELETE /api/v1/regions/{id}", "删除区域", "DELETE", False),
            ("007", "接入平台", "GET /api/v1/platforms", "获取接入平台", "GET", False),
            ("007", "接入平台", "POST /api/v1/platforms", "创建接入平台", "POST", False),
            ("007", "接入平台", "PUT /api/v1/platforms/{id}", "更新接入平台", "PUT", False),
            ("007", "接入平台", "DELETE /api/v1/platforms/{id}", "删除接入平台", "DELETE", False),

            # 数据清理 (008)
            ("008", "数据清理", "GET /api/v1/clean-records", "获取清理记录", "GET", False),
            ("008", "数据清理", "POST /api/v1/clean-records", "创建清理记录", "POST", False),
            ("008", "数据清理", "PUT /api/v1/clean-records/{id}", "更新清理记录", "PUT", False),
            ("008", "数据清理", "DELETE /api/v1/clean-records/{id}", "删除清理记录", "DELETE", False),

            # 监控服务 (009)
            ("009", "监控服务", "GET /api/v1/device-streams", "获取视频流", "GET", False),
            ("009", "监控服务", "POST /api/v1/device-streams", "创建视频流", "POST", False),
            ("009", "监控服务", "PUT /api/v1/device-streams/{id}", "更新视频流", "PUT", False),
            ("009", "监控服务", "DELETE /api/v1/device-streams/{id}", "删除视频流", "DELETE", False),

            # 固件服务 (011)
            ("011", "固件管理", "GET /api/v1/firmware", "获取固件列表", "GET", False),
            ("011", "固件管理", "POST /api/v1/firmware", "上传固件", "POST", False),
            ("011", "固件管理", "PUT /api/v1/firmware/{id}", "更新固件", "PUT", False),
            ("011", "固件管理", "DELETE /api/v1/firmware/{id}", "删除固件", "DELETE", False),

            # 部署服务 (012)
            ("012", "部署管理", "GET /api/v1/deployments", "获取部署列表", "GET", False),
            ("012", "部署管理", "POST /api/v1/deployments", "创建部署", "POST", False),
            ("012", "部署管理", "PUT /api/v1/deployments/{id}", "更新部署", "PUT", False),
            ("012", "部署管理", "DELETE /api/v1/deployments/{id}", "删除部署", "DELETE", False),
            ("012", "标注管理", "GET /api/v1/annotations", "获取标注列表", "GET", False),
            ("012", "标注管理", "POST /api/v1/annotations", "创建标注", "POST", False),
            ("012", "标注管理", "PUT /api/v1/annotations/{id}", "更新标注", "PUT", False),
            ("012", "标注管理", "DELETE /api/v1/annotations/{id}", "删除标注", "DELETE", False),

            # 数据看板 (013)
            ("013", "数据看板", "GET /api/v1/dashboard", "获取仪表盘数据", "GET", False),

            # 日志审计 (014)
            ("014", "日志审计", "GET /api/v1/operation-logs", "获取操作日志", "GET", False),
            ("014", "日志审计", "DELETE /api/v1/operation-logs/{id}", "删除操作日志", "DELETE", False),
            ("014", "日志审计", "POST /api/v1/operation-logs/batch-delete", "批量删除日志", "POST", False),

            # 任务调度 (015)
            ("015", "任务调度", "GET /api/v1/tasks", "获取任务列表", "GET", False),
            ("015", "任务调度", "POST /api/v1/tasks", "创建任务", "POST", False),
            ("015", "任务调度", "PUT /api/v1/tasks/{id}", "更新任务", "PUT", False),
            ("015", "任务调度", "DELETE /api/v1/tasks/{id}", "删除任务", "DELETE", False),
        ]

        for service_code, group, resource, desc, method, hidden in resources:
            db.add(Resource(
                resource=resource,
                resource_group=group,
                method=method,
                service_code=service_code,
                description=desc,
                hidden=hidden,
                created_at=now,
                updated_at=now
            ))

        await db.commit()
        print(f"Inserted {len(resources)} resources.")


if __name__ == "__main__":
    asyncio.run(seed_resources())

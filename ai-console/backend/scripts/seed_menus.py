import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.insert(0, r"E:\python\code\console\ai-console\backend")

from app.core.database import AsyncSessionLocal
from app.models.menu import Menu


async def seed_menus():
    async with AsyncSessionLocal() as db:
        # 检查是否已有数据
        from sqlalchemy import select, func
        count_result = await db.execute(select(func.count()).select_from(Menu).where(Menu.deleted_at.is_(None)))
        count = count_result.scalar()
        if count > 0:
            print(f"Menu table already has {count} records, skipping seed.")
            return

        now = datetime.utcnow()

        def make(**kwargs):
            return Menu(created_at=now, updated_at=now, **kwargs)

        # 根菜单
        monitor = make(name="monitor", path="/monitor", hidden=False, sort=1, component="Layout", title="监控中心", icon="Monitor")
        console = make(name="console", path="/console", hidden=False, sort=2, component="Layout", title="控制台", icon="Setting")
        data_clean = make(name="dataClean", path="/data-clean", hidden=False, sort=3, component="Layout", title="数据清理", icon="Delete")
        algorithm = make(name="algorithm", path="/algorithm", hidden=False, sort=4, component="Layout", title="算法管理", icon="Cpu")
        firmware = make(name="firmware", path="/firmware", hidden=False, sort=5, component="Layout", title="固件中心", icon="Box")
        events = make(name="events", path="/events", hidden=False, sort=6, component="Layout", title="预警事件", icon="Bell")

        db.add_all([monitor, console, data_clean, algorithm, firmware, events])
        await db.flush()

        # 监控中心子菜单
        monitor_children = [
            make(name="monitorSingle", path="/monitor/single", hidden=False, parent_id=monitor.id, sort=1, component="views/MenuPanel", title="实时监控", icon="VideoCamera"),
            make(name="monitorWall", path="/monitor/wall", hidden=False, parent_id=monitor.id, sort=2, component="views/MenuPanel", title="监控墙", icon="Monitor"),
            make(name="eventStats", path="/event-stats", hidden=False, parent_id=monitor.id, sort=3, component="views/MenuPanel", title="事件统计", icon="DataLine"),
            make(name="eventManage", path="/event-manage", hidden=False, parent_id=monitor.id, sort=4, component="views/MenuPanel", title="事件管理", icon="Document"),
            make(name="fileAnalysis", path="/file-analysis", hidden=False, parent_id=monitor.id, sort=5, component="views/MenuPanel", title="文件分析", icon="FolderOpened"),
        ]
        db.add_all(monitor_children)

        # 控制台 -> 超级管理
        super_admin = make(name="superAdmin", path="/console/super-admin", hidden=False, parent_id=console.id, sort=1, component="views/Console", title="超级管理", icon="Setting")
        db.add(super_admin)
        await db.flush()

        super_admin_items = [
            make(name="menuManage", path="/console/super-admin/menu-manage", hidden=False, parent_id=super_admin.id, sort=1, component="views/Console", title="菜单管理", icon="Menu"),
            make(name="resourceManage", path="/console/super-admin/resource-manage", hidden=False, parent_id=super_admin.id, sort=2, component="views/Console", title="资源管理", icon="Files"),
            make(name="microservice", path="/console/super-admin/microservice", hidden=False, parent_id=super_admin.id, sort=3, component="views/Console", title="微服务", icon="Monitor"),
            make(name="uiCustomize", path="/console/super-admin/ui-customize", hidden=False, parent_id=super_admin.id, sort=4, component="views/Console", title="UI定制", icon="Tools"),
            make(name="licenseFile", path="/console/super-admin/license-file", hidden=False, parent_id=super_admin.id, sort=5, component="views/Console", title="授权文件", icon="Key"),
        ]
        db.add_all(super_admin_items)

        # 控制台 -> 用户中心
        user_center = make(name="userCenter", path="/console/user-center", hidden=False, parent_id=console.id, sort=2, component="views/Console", title="用户中心", icon="User")
        db.add(user_center)
        await db.flush()

        user_center_items = [
            make(name="userManage", path="/console/user-center/user-manage", hidden=False, parent_id=user_center.id, sort=1, component="views/Console", title="用户管理", icon="UserFilled"),
            make(name="orgManage", path="/console/user-center/org-manage", hidden=False, parent_id=user_center.id, sort=2, component="views/Console", title="组织管理", icon="OfficeBuilding"),
            make(name="roleManage", path="/console/user-center/role-manage", hidden=False, parent_id=user_center.id, sort=3, component="views/Console", title="角色管理", icon="Key"),
            make(name="operationHistory", path="/console/user-center/operation-history", hidden=False, parent_id=user_center.id, sort=4, component="views/Console", title="操作历史", icon="Clock"),
        ]
        db.add_all(user_center_items)

        # 控制台 -> 设备管理
        device = make(name="deviceManage", path="/console/device", hidden=False, parent_id=console.id, sort=3, component="views/Console", title="设备管理", icon="Cpu")
        db.add(device)
        await db.flush()

        device_items = [
            make(name="dataSource", path="/console/device/data-source", hidden=False, parent_id=device.id, sort=1, component="views/Console", title="数据源", icon="Upload"),
            make(name="deviceGroup", path="/console/device/device-group", hidden=False, parent_id=device.id, sort=2, component="views/Console", title="设备组管理", icon="Grid"),
            make(name="region", path="/console/device/region", hidden=False, parent_id=device.id, sort=3, component="views/Console", title="区域", icon="Location"),
            make(name="platformList", path="/console/device/device-access/platform-list", hidden=False, parent_id=device.id, sort=4, component="views/Console", title="接入平台", icon="Connection"),
            make(name="gb28181", path="/console/device/device-access/gb28181", hidden=False, parent_id=device.id, sort=5, component="views/Console", title="GB28181", icon="VideoCamera"),
            make(name="onvif", path="/console/device/device-access/onvif", hidden=False, parent_id=device.id, sort=6, component="views/Console", title="ONVIF", icon="Monitor"),
        ]
        db.add_all(device_items)

        # 控制台 -> 联动管理
        linkage = make(name="linkage", path="/console/linkage", hidden=False, parent_id=console.id, sort=4, component="views/Console", title="联动管理", icon="Connection")
        db.add(linkage)
        await db.flush()

        linkage_items = [
            make(name="sendNotify", path="/console/linkage/send-notify", hidden=False, parent_id=linkage.id, sort=1, component="views/Console", title="发送通知", icon="Bell"),
            make(name="linkageRule", path="/console/linkage/linkage-rule", hidden=False, parent_id=linkage.id, sort=2, component="views/Console", title="联动规则", icon="Operation"),
            make(name="pushHistory", path="/console/linkage/push-history", hidden=False, parent_id=linkage.id, sort=3, component="views/Console", title="推送历史", icon="Promotion"),
        ]
        db.add_all(linkage_items)

        # 控制台 -> 系统管理
        system = make(name="systemManage", path="/console/system", hidden=False, parent_id=console.id, sort=5, component="views/Console", title="系统管理", icon="Tools")
        db.add(system)
        await db.flush()

        system_items = [
            make(name="videoSetting", path="/console/system/video-setting", hidden=False, parent_id=system.id, sort=1, component="views/Console", title="录像设置", icon="VideoCamera"),
            make(name="fileManager", path="/console/system/file-manager", hidden=False, parent_id=system.id, sort=2, component="views/Console", title="文件管理", icon="Folder"),
            make(name="helpCenter", path="/console/system/help-center", hidden=False, parent_id=system.id, sort=3, component="views/Console", title="帮助中心", icon="QuestionFilled"),
            make(name="popupSetting", path="/console/system/popup-setting", hidden=False, parent_id=system.id, sort=4, component="views/Console", title="弹窗设置", icon="Bell"),
            make(name="disposeTag", path="/console/system/dispose-tag", hidden=False, parent_id=system.id, sort=5, component="views/Console", title="处置标签", icon="PriceTag"),
        ]
        db.add_all(system_items)

        # 控制台 -> 算法管理
        algo = make(name="algoManage", path="/console/algorithm", hidden=False, parent_id=console.id, sort=6, component="views/Console", title="算法管理", icon="Cpu")
        db.add(algo)
        await db.flush()

        algo_items = [
            make(name="algorithmManage", path="/console/algorithm/algorithm-manage", hidden=False, parent_id=algo.id, sort=1, component="views/Console", title="算法管理", icon="Cpu"),
            make(name="algoEventManage", path="/console/algorithm/event-manage", hidden=False, parent_id=algo.id, sort=2, component="views/Console", title="事件管理", icon="Document"),
            make(name="algoService", path="/console/algorithm/algorithm-service", hidden=False, parent_id=algo.id, sort=3, component="views/Console", title="算法服务", icon="Monitor"),
        ]
        db.add_all(algo_items)

        # 独立的叶子根菜单
        leaf_roots = [
            make(name="dataCleanPage", path="/data-clean", hidden=False, parent_id=data_clean.id, sort=1, component="views/Console", title="数据清理", icon="Delete"),
            make(name="firmwarePage", path="/firmware", hidden=False, parent_id=firmware.id, sort=1, component="views/Console", title="固件中心", icon="Box"),
            make(name="eventsPage", path="/events", hidden=False, parent_id=events.id, sort=1, component="views/Console", title="预警事件", icon="Bell"),
        ]
        db.add_all(leaf_roots)

        await db.commit()
        print("Menu seed completed!")


if __name__ == "__main__":
    asyncio.run(seed_menus())

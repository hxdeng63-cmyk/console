"""Database seed script for ai-console backend.

Usage:
    python -m app.seed
    python -m app.seed --clear

--clear: Truncate all tables and re-insert data.
"""

import argparse
import asyncio
import random
from datetime import datetime, time, timedelta

from faker import Faker
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.models import (
    Organization,
    User,
    Role,
    Menu,
    Resource,
    UserRole,
    RoleMenu,
    RoleResource,
    Region,
    Device,
    DeviceStream,
    DeviceGroup,
    DeviceGroupMembership,
    Algorithm,
    EventType,
    AlgorithmService,
    Deployment,
    DeploymentDevice,
    DeploymentSchedule,
    WarningEvent,
    LinkageRule,
    LinkageRuleDevice,
    PushHistory,
    Task,
    TaskDevice,
    VideoSetting,
    File,
    DisposeTag,
    WarningEventTag,
    License,
    Firmware,
    OperationLog,
    CleanRecord,
    PopupSetting,
    PopupEventLimit,
    UITheme,
    Microservice,
    AccessPlatform,
    Gb28181Device,
    OnvifDevice,
    Annotation,
    Preset,
    WarningEventArchive,
)

fake = Faker(["zh_CN", "en_US"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def random_datetime(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


async def count_rows(session: AsyncSession, model) -> int:
    result = await session.execute(select(func.count()).select_from(model))
    return result.scalar() or 0


async def truncate_all(session: AsyncSession):
    """Truncate all tables (PostgreSQL specific)."""
    tables = [
        "warning_event_archive",
        "warning_event_tag",
        "warning_event",
        "push_history",
        "linkage_rule_device",
        "linkage_rule",
        "deployment_schedule",
        "deployment_device",
        "deployment",
        "annotation",
        "preset",
        "device_stream",
        "gb28181_device",
        "onvif_device",
        "task_device",
        "task",
        "video_setting",
        "popup_event_limit",
        "popup_setting",
        "file",
        "clean_record",
        "operation_log",
        "device_group_membership",
        "device_group",
        "device",
        "region",
        "access_platform",
        "algorithm_service",
        "event_type",
        "algorithm",
        "role_resource",
        "role_menu",
        "user_role",
        "user",
        "role",
        "resource",
        "menu",
        "organization",
        "firmware",
        "license",
        "ui_theme",
        "microservice",
    ]
    for t in tables:
        await session.execute(text(f'TRUNCATE TABLE "{t}" RESTART IDENTITY CASCADE'))
    await session.commit()


# ---------------------------------------------------------------------------
# Seed functions
# ---------------------------------------------------------------------------


async def seed_organizations(session: AsyncSession) -> list[int]:
    if await count_rows(session, Organization):
        result = await session.execute(select(Organization.id))
        return [r[0] for r in result.all()]

    roots = [
        Organization(name="总部", code="HQ", level=1, sort=1),
        Organization(name="华东分部", code="EAST", level=1, sort=2),
        Organization(name="华南分部", code="SOUTH", level=1, sort=3),
    ]
    session.add_all(roots)
    await session.flush()

    children = [
        Organization(name="上海研发中心", code="SH-RD", level=2, sort=1, parent_id=roots[1].id),
        Organization(name="杭州办事处", code="HZ-OF", level=2, sort=2, parent_id=roots[1].id),
        Organization(name="深圳研发中心", code="SZ-RD", level=2, sort=1, parent_id=roots[2].id),
        Organization(name="广州办事处", code="GZ-OF", level=2, sort=2, parent_id=roots[2].id),
    ]
    session.add_all(children)
    await session.flush()

    result = await session.execute(select(Organization.id))
    return [r[0] for r in result.all()]


async def seed_roles(session: AsyncSession) -> list[int]:
    if await count_rows(session, Role):
        result = await session.execute(select(Role.id))
        return [r[0] for r in result.all()]

    roles = [
        Role(name="超级管理员", code="super_admin", description="系统最高权限"),
        Role(name="管理员", code="admin", description="日常管理权限"),
        Role(name="运维工程师", code="ops", description="设备运维权限"),
        Role(name="普通用户", code="user", description="查看权限"),
        Role(name="审计员", code="auditor", description="日志审计权限"),
    ]
    session.add_all(roles)
    await session.flush()
    return [r.id for r in roles]


async def seed_users(session: AsyncSession, org_ids: list[int], role_ids: list[int]) -> list[int]:
    if await count_rows(session, User):
        result = await session.execute(select(User.id))
        return [r[0] for r in result.all()]

    chinese_names = [
        "张伟", "李娜", "王强", "刘洋", "陈静", "杨帆", "赵敏", "黄磊", "周杰", "吴倩",
        "徐鹏", "孙丽", "朱伟", "马芳", "胡军", "郭明", "林秀", "何平", "高飞", "郑宇",
        "谢薇", "宋涛", "唐敏", "许强", "韩磊", "冯丹", "曹阳", "彭亮", "曾洁", "董辉",
    ]

    users = []
    for i in range(30):
        org_id = random.choice(org_ids) if org_ids else None
        users.append(
            User(
                username=f"user{i+1:03d}",
                real_name=chinese_names[i] if i < len(chinese_names) else fake.name(),
                password="$2b$12$dummyhashedpassword",
                phone=fake.phone_number()[:20],
                email=fake.email(),
                gender=random.choice(["male", "female", None]),
                org_id=org_id,
                status=random.choice(["active", "active", "active", "inactive"]),
            )
        )
    session.add_all(users)
    await session.flush()
    user_ids = [u.id for u in users]

    # Assign roles - ensure each user has at least one role
    user_roles = []
    for uid in user_ids:
        # Primary role
        user_roles.append(UserRole(user_id=uid, role_id=random.choice(role_ids)))
        # 30% chance of secondary role
        if random.random() < 0.3:
            second_role = random.choice(role_ids)
            # Avoid duplicate roles for same user
            if second_role != user_roles[-1].role_id:
                user_roles.append(UserRole(user_id=uid, role_id=second_role))
    session.add_all(user_roles)
    await session.flush()
    return user_ids


async def seed_menus(session: AsyncSession) -> list[int]:
    if await count_rows(session, Menu):
        result = await session.execute(select(Menu.id))
        return [r[0] for r in result.all()]

    menus = [
        Menu(name="首页", path="/dashboard", sort=1, component="Dashboard", title="首页", icon="HomeFilled"),
        Menu(name="设备管理", path="/device", sort=2, component="Layout", title="设备管理", icon="VideoCamera"),
        Menu(name="设备列表", path="/device/list", sort=1, parent_id=None, component="DeviceList", title="设备列表", icon="List"),
        Menu(name="设备分组", path="/device/group", sort=2, parent_id=None, component="DeviceGroup", title="设备分组", icon="FolderOpened"),
        Menu(name="区域管理", path="/device/region", sort=3, parent_id=None, component="Region", title="区域管理", icon="MapLocation"),
        Menu(name="算法管理", path="/algorithm", sort=3, component="Layout", title="算法管理", icon="Cpu"),
        Menu(name="算法列表", path="/algorithm/list", sort=1, parent_id=None, component="AlgorithmList", title="算法列表", icon="Grid"),
        Menu(name="事件类型", path="/algorithm/event", sort=2, parent_id=None, component="EventType", title="事件类型", icon="Bell"),
        Menu(name="布控管理", path="/deployment", sort=4, component="Deployment", title="布控管理", icon="Aim"),
        Menu(name="联动规则", path="/linkage", sort=5, component="Layout", title="联动规则", icon="Link"),
        Menu(name="规则列表", path="/linkage/rule", sort=1, parent_id=None, component="LinkageRule", title="规则列表", icon="Document"),
        Menu(name="推送历史", path="/linkage/history", sort=2, parent_id=None, component="PushHistory", title="推送历史", icon="Timer"),
        Menu(name="系统设置", path="/system", sort=6, component="Layout", title="系统设置", icon="Setting"),
        Menu(name="视频设置", path="/system/video", sort=1, parent_id=None, component="VideoSetting", title="视频设置", icon="VideoPlay"),
        Menu(name="文件管理", path="/system/file", sort=2, parent_id=None, component="FileManager", title="文件管理", icon="Folder"),
        Menu(name="用户中心", path="/user", sort=7, component="Layout", title="用户中心", icon="User"),
        Menu(name="用户管理", path="/user/list", sort=1, parent_id=None, component="UserList", title="用户管理", icon="UserFilled"),
        Menu(name="角色管理", path="/user/role", sort=2, parent_id=None, component="RoleManage", title="角色管理", icon="Medal"),
        Menu(name="组织管理", path="/user/org", sort=3, parent_id=None, component="OrgManage", title="组织管理", icon="OfficeBuilding"),
    ]
    session.add_all(menus)
    await session.flush()

    # Fix parent_ids for nested menus
    name_to_id = {m.name: m.id for m in menus}
    parent_map = {
        "设备列表": "设备管理",
        "设备分组": "设备管理",
        "区域管理": "设备管理",
        "算法列表": "算法管理",
        "事件类型": "算法管理",
        "规则列表": "联动规则",
        "推送历史": "联动规则",
        "视频设置": "系统设置",
        "文件管理": "系统设置",
        "用户管理": "用户中心",
        "角色管理": "用户中心",
        "组织管理": "用户中心",
    }
    for child_name, parent_name in parent_map.items():
        menu = next(m for m in menus if m.name == child_name)
        menu.parent_id = name_to_id[parent_name]
    await session.flush()

    result = await session.execute(select(Menu.id))
    return [r[0] for r in result.all()]


async def seed_resources(session: AsyncSession) -> list[int]:
    if await count_rows(session, Resource):
        result = await session.execute(select(Resource.id))
        return [r[0] for r in result.all()]

    groups = ["device", "algorithm", "deployment", "linkage", "system", "user", "monitor"]
    resources = []
    for g in groups:
        for method in ["GET", "POST", "PUT", "DELETE"]:
            resources.append(
                Resource(
                    resource=f"/api/v1/{g}",
                    resource_group=g,
                    method=method,
                    description=f"{g} {method}",
                )
            )
    session.add_all(resources)
    await session.flush()
    return [r.id for r in resources]


async def seed_role_permissions(session: AsyncSession, role_ids: list[int], menu_ids: list[int], resource_ids: list[int]):
    # Role-Menu
    if not await count_rows(session, RoleMenu):
        rm = []
        for rid in role_ids:
            for mid in random.sample(menu_ids, k=min(len(menu_ids), random.randint(3, len(menu_ids)))):
                rm.append(RoleMenu(role_id=rid, menu_id=mid))
        session.add_all(rm)
        await session.flush()

    # Role-Resource
    if not await count_rows(session, RoleResource):
        rr = []
        for rid in role_ids:
            for resid in random.sample(resource_ids, k=min(len(resource_ids), random.randint(5, len(resource_ids)))):
                rr.append(RoleResource(role_id=rid, resource_id=resid))
        session.add_all(rr)
        await session.flush()


async def seed_regions(session: AsyncSession) -> list[int]:
    if await count_rows(session, Region):
        result = await session.execute(select(Region.id))
        return [r[0] for r in result.all()]

    roots = [
        Region(name="北京市", code="110000", level=1, sort=1),
        Region(name="上海市", code="310000", level=1, sort=2),
        Region(name="广东省", code="440000", level=1, sort=3),
        Region(name="浙江省", code="330000", level=1, sort=4),
        Region(name="江苏省", code="320000", level=1, sort=5),
    ]
    session.add_all(roots)
    await session.flush()

    children = [
        Region(name="朝阳区", code="110105", level=2, sort=1, parent_id=roots[0].id),
        Region(name="海淀区", code="110108", level=2, sort=2, parent_id=roots[0].id),
        Region(name="浦东新区", code="310115", level=2, sort=1, parent_id=roots[1].id),
        Region(name="徐汇区", code="310104", level=2, sort=2, parent_id=roots[1].id),
        Region(name="深圳市", code="440300", level=2, sort=1, parent_id=roots[2].id),
        Region(name="广州市", code="440100", level=2, sort=2, parent_id=roots[2].id),
        Region(name="杭州市", code="330100", level=2, sort=1, parent_id=roots[3].id),
        Region(name="宁波市", code="330200", level=2, sort=2, parent_id=roots[3].id),
        Region(name="南京市", code="320100", level=2, sort=1, parent_id=roots[4].id),
        Region(name="苏州市", code="320500", level=2, sort=2, parent_id=roots[4].id),
    ]
    session.add_all(children)
    await session.flush()

    result = await session.execute(select(Region.id))
    return [r[0] for r in result.all()]


async def seed_access_platforms(session: AsyncSession) -> list[int]:
    if await count_rows(session, AccessPlatform):
        result = await session.execute(select(AccessPlatform.id))
        return [r[0] for r in result.all()]

    platforms = []
    platform_types = ["GB28181", "ONVIF", "RTSP", "RTMP"]
    for i in range(15):
        ptype = random.choice(platform_types)
        config = {}
        if ptype == "GB28181":
            config = {"sip_server_id": f"3402000000200000000{i+1}", "sip_domain": "3402000000"}
        elif ptype == "ONVIF":
            config = {"discovery_timeout": 5, "probe_interval": 30}
        elif ptype == "RTSP":
            config = {"transport": "tcp", "buffer_size": 4096}
        else:
            config = {"app": "live", "stream_timeout": 60}
        platforms.append(
            AccessPlatform(
                name=f"{ptype}平台-{i+1:02d}",
                type=ptype,
                version=f"v{random.randint(1,5)}.{random.randint(0,9)}",
                device_count=random.randint(0, 50),
                status=random.choice(["active", "active", "inactive"]),
                config_json=config,
            )
        )
    session.add_all(platforms)
    await session.flush()
    return [p.id for p in platforms]


async def seed_algorithms(session: AsyncSession) -> list[int]:
    if await count_rows(session, Algorithm):
        result = await session.execute(select(Algorithm.id))
        return [r[0] for r in result.all()]

    algo_data = [
        ("交通算法", "detection", "交通", "交通事件检测与流量统计", [
            ("疑似事故", "检测到疑似交通事故"),
            ("作业人员", "检测到道路作业人员"),
            ("交通阻塞", "检测到交通阻塞"),
            ("异常停车", "检测到异常停车行为"),
            ("烟雾", "检测到烟雾"),
            ("作业车辆识别", "识别到作业车辆"),
            ("非机动车驶入", "检测到非机动车驶入"),
            ("占用应急车道", "检测到占用应急车道"),
            ("逆向行驶", "检测到逆向行驶"),
            ("通过卡车数量", "统计通过卡车数量"),
            ("通过大客车数量", "统计通过大客车数量"),
            ("通过摩托车数量", "统计通过摩托车数量"),
            ("通过小汽车数量", "统计通过小汽车数量"),
            ("下行车流量", "统计下行车流量"),
            ("上行车流量", "统计上行车流量"),
            ("行人闯入", "检测到行人闯入"),
        ]),
    ]
    algorithms = []
    for n, t, b, d, _ in algo_data:
        algorithms.append(Algorithm(name=n, type=t, business_category=b, description=d))
    session.add_all(algorithms)
    await session.flush()

    # Create event types linked to each algorithm
    event_types = []
    for algo, (_, _, _, _, events) in zip(algorithms, algo_data):
        for ev_name, ev_desc in events:
            event_types.append(EventType(
                algorithm_id=algo.id,
                name=ev_name,
                description=ev_desc,
                category=random.choice(["detection", "analysis", "alarm"]),
                severity=random.randint(2, 5),
            ))
    session.add_all(event_types)
    await session.flush()

    return [a.id for a in algorithms]


async def seed_event_types(session: AsyncSession, algorithm_ids: list[int]) -> list[int]:
    """Event types are now created within seed_algorithms for deterministic mapping.
    This function ensures event types exist and returns their IDs."""
    result = await session.execute(select(EventType.id))
    ids = [r[0] for r in result.all()]
    if ids:
        return ids

    # Fallback: create generic event types if seed_algorithms didn't run
    event_names = [
        ("人脸出现", 3),
        ("陌生人告警", 4),
        ("车辆违停", 3),
        ("车辆逆行", 4),
        ("区域入侵", 4),
        ("越界检测", 3),
        ("烟火告警", 5),
        ("烟雾检测", 4),
        ("打架斗殴", 5),
        ("人员聚集", 3),
        ("安全帽未佩戴", 3),
        ("反光衣未穿", 3),
        ("人员摔倒", 4),
        ("徘徊检测", 2),
        ("物品遗留", 3),
    ]
    event_types = []
    for name, severity in event_names:
        event_types.append(
            EventType(
                algorithm_id=random.choice(algorithm_ids) if algorithm_ids else None,
                name=name,
                description=fake.sentence(),
                category=random.choice(["detection", "analysis", "alarm"]),
                severity=severity,
            )
        )
    session.add_all(event_types)
    await session.flush()
    return [e.id for e in event_types]


async def seed_algorithm_services(session: AsyncSession) -> list[int]:
    if await count_rows(session, AlgorithmService):
        result = await session.execute(select(AlgorithmService.id))
        return [r[0] for r in result.all()]

    services = []
    for i in range(12):
        services.append(
            AlgorithmService(
                service_id=f"svc-{i+1:03d}",
                service_name=f"算法服务-{i+1:02d}",
                service_code=f"algo-service-{i+1}",
                service_ip=fake.ipv4_private(),
                service_port=random.randint(8000, 9000),
                annotation_ip=fake.ipv4_private(),
                annotation_port=random.randint(9001, 9999),
                status=random.choice(["active", "active", "active", "inactive"]),
            )
        )
    session.add_all(services)
    await session.flush()
    return [s.id for s in services]


async def seed_devices(
    session: AsyncSession, region_ids: list[int], org_ids: list[int]
) -> list[int]:
    if await count_rows(session, Device):
        result = await session.execute(select(Device.id))
        return [r[0] for r in result.all()]

    device_types = ["IPC", "NVR", "DVR", "球机", "枪机", "半球"]
    access_types = ["direct", "GB28181", "ONVIF", "RTSP"]
    statuses = ["active", "active", "active", "inactive", "offline"]

    devices = []
    for i in range(50):
        devices.append(
            Device(
                device_code=f"DEV{datetime.now().year}{i+1:05d}",
                name=f"{fake.street_name()}摄像头-{i+1:03d}",
                status=random.choice(statuses),
                access_type=random.choice(access_types),
                device_type=random.choice(device_types),
                longitude=round(random.uniform(113.0, 122.0), 7),
                latitude=round(random.uniform(22.0, 32.0), 7),
                region_id=random.choice(region_ids) if region_ids else None,
                org_id=random.choice(org_ids) if org_ids else None,
                memory_usage=round(random.uniform(10.0, 95.0), 2),
                disk_size=random.choice([128, 256, 512, 1024, 2048]) * 1024 * 1024 * 1024,
                disk_usage=round(random.uniform(20.0, 90.0), 2),
                remark=fake.sentence() if random.random() < 0.5 else None,
            )
        )
    session.add_all(devices)
    await session.flush()
    return [d.id for d in devices]


async def seed_device_streams(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, DeviceStream):
        return
    streams = []
    resolutions = ["1920x1080", "1280x720", "2560x1440", "3840x2160"]
    codecs = ["H264", "H265"]
    for did in device_ids:
        for j in range(random.randint(1, 3)):
            streams.append(
                DeviceStream(
                    device_id=did,
                    stream_type="main" if j == 0 else "sub",
                    stream_url=f"rtsp://{fake.ipv4_private()}:554/stream{j}",
                    push_url=f"rtmp://{fake.ipv4_private()}:1935/live/stream{did}_{j}",
                    resolution=random.choice(resolutions),
                    fps=random.choice([15, 25, 30]),
                    codec=random.choice(codecs),
                    is_primary=j == 0,
                    status=random.choice(["active", "active", "inactive"]),
                )
            )
    session.add_all(streams)
    await session.flush()


async def seed_device_groups(session: AsyncSession) -> list[int]:
    if await count_rows(session, DeviceGroup):
        result = await session.execute(select(DeviceGroup.id))
        return [r[0] for r in result.all()]

    roots = [
        DeviceGroup(group_code="GRP-001", name="重点区域", device_count=0, remark="核心监控区域"),
        DeviceGroup(group_code="GRP-002", name="普通区域", device_count=0, remark="一般监控区域"),
        DeviceGroup(group_code="GRP-003", name="停车场", device_count=0, remark="停车场监控"),
    ]
    session.add_all(roots)
    await session.flush()

    children = [
        DeviceGroup(group_code="GRP-001-01", name="大门出入口", device_count=0, parent_id=roots[0].id),
        DeviceGroup(group_code="GRP-001-02", name="办公楼", device_count=0, parent_id=roots[0].id),
        DeviceGroup(group_code="GRP-002-01", name="园区周界", device_count=0, parent_id=roots[1].id),
        DeviceGroup(group_code="GRP-003-01", name="地下停车场", device_count=0, parent_id=roots[2].id),
    ]
    session.add_all(children)
    await session.flush()

    result = await session.execute(select(DeviceGroup.id))
    return [r[0] for r in result.all()]


async def seed_device_group_memberships(session: AsyncSession, group_ids: list[int], device_ids: list[int]):
    if await count_rows(session, DeviceGroupMembership):
        return
    memberships = []
    for did in device_ids:
        if random.random() < 0.6:
            memberships.append(
                DeviceGroupMembership(device_group_id=random.choice(group_ids), device_id=did)
            )
    session.add_all(memberships)
    await session.flush()


async def seed_deployments(
    session: AsyncSession,
    algorithm_ids: list[int],
    service_ids: list[int],
    device_ids: list[int],
) -> list[int]:
    if await count_rows(session, Deployment):
        result = await session.execute(select(Deployment.id))
        return [r[0] for r in result.all()]

    statuses = ["active", "active", "paused", "stopped"]
    algo_statuses = ["running", "running", "stopped", "error"]
    deployments = []
    for i in range(20):
        deployments.append(
            Deployment(
                name=f"布控任务-{i+1:02d}",
                algorithm_id=random.choice(algorithm_ids) if algorithm_ids else None,
                service_id=random.choice(service_ids) if service_ids else None,
                status=random.choice(statuses),
                algorithm_status=random.choice(algo_statuses),
                deployed_at=random_datetime(datetime(2024, 1, 1), datetime.now()),
            )
        )
    session.add_all(deployments)
    await session.flush()
    dep_ids = [d.id for d in deployments]

    # Deployment-Device links
    dd_links = []
    for dep in deployments:
        for _ in range(random.randint(1, 5)):
            dd_links.append(DeploymentDevice(deployment_id=dep.id, device_id=random.choice(device_ids)))
    session.add_all(dd_links)
    await session.flush()

    # Deployment schedules
    schedules = []
    for dep in deployments:
        for dow in range(7):
            if random.random() < 0.8:
                start = time(random.randint(0, 8), random.randint(0, 59))
                end = time(random.randint(16, 23), random.randint(0, 59))
                schedules.append(
                    DeploymentSchedule(deployment_id=dep.id, day_of_week=dow, start_time=start, end_time=end)
                )
    session.add_all(schedules)
    await session.flush()
    return dep_ids


async def seed_annotations(session: AsyncSession, deployment_ids: list[int], device_ids: list[int]):
    if await count_rows(session, Annotation):
        return
    annotations = []
    colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF"]
    types = ["monitoring", "restricted", "alarm"]
    for i in range(30):
        polygon = {
            "points": [
                {"x": random.randint(0, 1920), "y": random.randint(0, 1080)} for _ in range(random.randint(3, 8))
            ]
        }
        annotations.append(
            Annotation(
                deployment_id=random.choice(deployment_ids) if deployment_ids else None,
                device_id=random.choice(device_ids) if device_ids else None,
                name=f"标注区域-{i+1:02d}",
                type=random.choice(types),
                polygon_json=polygon,
                color=random.choice(colors),
            )
        )
    session.add_all(annotations)
    await session.flush()


async def seed_linkage_rules(
    session: AsyncSession,
    algorithm_ids: list[int],
    event_type_ids: list[int],
    device_ids: list[int],
) -> list[int]:
    if await count_rows(session, LinkageRule):
        result = await session.execute(select(LinkageRule.id))
        return [r[0] for r in result.all()]

    action_types = ["push", "email", "sms", "webhook", "snapshot"]
    statuses = ["active", "active", "active", "inactive"]
    rules = []
    for i in range(25):
        rules.append(
            LinkageRule(
                rule_name=f"联动规则-{i+1:02d}",
                trigger_mode=random.choice(["AUTO", "MANUAL"]),
                algorithm_id=random.choice(algorithm_ids) if algorithm_ids else None,
                event_type_id=random.choice(event_type_ids) if event_type_ids else None,
                level=random.randint(1, 5),
                delay_push=random.choice([0, 0, 5, 10, 30]),
                is_compliant=random.choice(["compliant", "non_compliant", None]),
                unit=fake.company(),
                action_type=random.choice(action_types),
                status=random.choice(statuses),
                link=fake.url() if random.random() < 0.3 else None,
                content=fake.sentence(),
                importance_level=random.randint(1, 5),
                send_frequency=random.choice(["immediate", "5min", "15min", "1hour"]),
                push_channels={"app": True, "sms": random.random() < 0.5, "email": random.random() < 0.5},
                app_id=fake.uuid4() if random.random() < 0.3 else None,
                app_secret=fake.password() if random.random() < 0.3 else None,
                template_id=fake.uuid4() if random.random() < 0.3 else None,
                push_target=fake.phone_number() if random.random() < 0.3 else None,
                remark=fake.sentence() if random.random() < 0.5 else None,
            )
        )
    session.add_all(rules)
    await session.flush()
    rule_ids = [r.id for r in rules]

    # LinkageRule-Device links
    lrd_links = []
    for rule in rules:
        for _ in range(random.randint(1, 4)):
            lrd_links.append(LinkageRuleDevice(linkage_rule_id=rule.id, device_id=random.choice(device_ids)))
    session.add_all(lrd_links)
    await session.flush()
    return rule_ids


async def seed_warning_events(
    session: AsyncSession,
    device_ids: list[int],
    org_ids: list[int],
    region_ids: list[int],
    algorithm_ids: list[int],
    event_type_ids: list[int],
    rule_ids: list[int],
) -> list[int]:
    if await count_rows(session, WarningEvent):
        result = await session.execute(select(WarningEvent.id))
        return [r[0] for r in result.all()]

    process_statuses = ["pending", "pending", "processing", "resolved", "ignored"]
    events = []
    for i in range(100):
        events.append(
            WarningEvent(
                device_id=random.choice(device_ids) if device_ids else None,
                org_id=random.choice(org_ids) if org_ids else None,
                region_id=random.choice(region_ids) if region_ids else None,
                algorithm_id=random.choice(algorithm_ids) if algorithm_ids else None,
                event_type_id=random.choice(event_type_ids) if event_type_ids else None,
                rule_id=random.choice(rule_ids) if rule_ids else None,
                event_detail=fake.sentence(),
                process_status=random.choice(process_statuses),
                is_compliant=random.choice([True, False, None]),
                report_time=random_datetime(datetime(2024, 6, 1), datetime.now()),
                image_url=f"https://example.com/images/event_{i+1:03d}.jpg" if random.random() < 0.7 else None,
                video_url=f"https://example.com/videos/event_{i+1:03d}.mp4" if random.random() < 0.3 else None,
            )
        )
    session.add_all(events)
    await session.flush()
    return [e.id for e in events]


async def seed_push_histories(
    session: AsyncSession,
    rule_ids: list[int],
    device_ids: list[int],
    event_type_ids: list[int],
):
    if await count_rows(session, PushHistory):
        return
    statuses = ["success", "success", "success", "failed", "pending"]
    histories = []
    for i in range(50):
        histories.append(
            PushHistory(
                rule_id=random.choice(rule_ids) if rule_ids else None,
                device_id=random.choice(device_ids) if device_ids else None,
                event_type_id=random.choice(event_type_ids) if event_type_ids else None,
                push_channels={"app": True, "sms": random.random() < 0.3},
                push_target=fake.phone_number(),
                push_time=random_datetime(datetime(2024, 6, 1), datetime.now()),
                status=random.choice(statuses),
                retry_count=random.randint(0, 3),
                operator=random.choice([None, fake.name()]),
                count=random.randint(1, 10),
                detail=fake.sentence(),
            )
        )
    session.add_all(histories)
    await session.flush()


async def seed_tasks(session: AsyncSession, algorithm_ids: list[int], device_ids: list[int]) -> list[int]:
    if await count_rows(session, Task):
        result = await session.execute(select(Task.id))
        return [r[0] for r in result.all()]

    trigger_rules = ["0 0 * * *", "*/5 * * * *", "0 8,20 * * *", "0 0 * * 0"]
    statuses = ["active", "active", "paused", "stopped"]
    tasks = []
    for i in range(15):
        tasks.append(
            Task(
                task_name=f"定时任务-{i+1:02d}",
                trigger_type=random.choice(["cron", "interval"]),
                trigger_rule=random.choice(trigger_rules),
                algorithm_id=random.choice(algorithm_ids) if algorithm_ids else None,
                status=random.choice(statuses),
                last_run_time=random_datetime(datetime(2024, 6, 1), datetime.now()) if random.random() < 0.7 else None,
            )
        )
    session.add_all(tasks)
    await session.flush()
    task_ids = [t.id for t in tasks]

    # Task-Device links
    td_links = []
    for task in tasks:
        for _ in range(random.randint(1, 5)):
            td_links.append(TaskDevice(task_id=task.id, device_id=random.choice(device_ids)))
    session.add_all(td_links)
    await session.flush()
    return task_ids


async def seed_video_settings(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, VideoSetting):
        return
    settings = []
    event_type_samples = [
        {"face": True, "vehicle": False},
        {"intrusion": True, "fire": True},
        {"crowd": False, "fall": True},
    ]
    for did in device_ids[:30]:
        settings.append(
            VideoSetting(
                device_id=did,
                event_types=random.choice(event_type_samples),
                record_duration_seconds=random.choice([10, 15, 30, 60]),
                status=random.choice([True, True, False]),
            )
        )
    session.add_all(settings)
    await session.flush()


async def seed_files(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, File):
        return
    file_types = ["video", "image", "log"]
    files = []
    for i in range(40):
        ftype = random.choice(file_types)
        ext = "mp4" if ftype == "video" else "jpg" if ftype == "image" else "log"
        size = random.randint(1024, 500 * 1024 * 1024)
        files.append(
            File(
                file_name=f"{fake.word()}_{i+1:03d}.{ext}",
                file_size_bytes=size,
                duration_seconds=random.randint(10, 300) if ftype == "video" else None,
                device_id=random.choice(device_ids) if device_ids else None,
                file_type=ftype,
                storage_path=f"/data/files/{ftype}/{i+1:03d}.{ext}",
                url=f"https://example.com/files/{ftype}/{i+1:03d}.{ext}",
            )
        )
    session.add_all(files)
    await session.flush()


async def seed_dispose_tags(session: AsyncSession) -> list[int]:
    if await count_rows(session, DisposeTag):
        result = await session.execute(select(DisposeTag.id))
        return [r[0] for r in result.all()]

    tags = [
        DisposeTag(tag_name="已处理", tag_color="#67C23A", usage_count=0),
        DisposeTag(tag_name="待核实", tag_color="#E6A23C", usage_count=0),
        DisposeTag(tag_name="误报", tag_color="#909399", usage_count=0),
        DisposeTag(tag_name="紧急", tag_color="#F56C6C", usage_count=0),
        DisposeTag(tag_name="需跟进", tag_color="#409EFF", usage_count=0),
        DisposeTag(tag_name="已归档", tag_color="#909399", usage_count=0),
    ]
    session.add_all(tags)
    await session.flush()
    return [t.id for t in tags]


async def seed_warning_event_tags(session: AsyncSession, event_ids: list[int], tag_ids: list[int]):
    if await count_rows(session, WarningEventTag):
        return
    wets = []
    for eid in event_ids:
        if random.random() < 0.4:
            wets.append(WarningEventTag(warning_event_id=eid, dispose_tag_id=random.choice(tag_ids)))
    session.add_all(wets)
    await session.flush()


async def seed_licenses(session: AsyncSession):
    if await count_rows(session, License):
        return
    licenses = [
        License(
            license_key=fake.uuid4(),
            type="enterprise",
            device_limit=500,
            used_count=random.randint(50, 400),
            expire_date=datetime(2026, 12, 31).date(),
            status="active",
        ),
        License(
            license_key=fake.uuid4(),
            type="trial",
            device_limit=50,
            used_count=random.randint(10, 45),
            expire_date=datetime(2025, 6, 30).date(),
            status="active",
        ),
    ]
    session.add_all(licenses)
    await session.flush()


async def seed_firmwares(session: AsyncSession):
    if await count_rows(session, Firmware):
        return
    firmwares = []
    device_types = ["IPC", "NVR", "DVR", "球机"]
    for i in range(15):
        firmwares.append(
            Firmware(
                name=f"固件升级包-{i+1:02d}",
                version=f"v{random.randint(1,5)}.{random.randint(0,9)}.{random.randint(0,99)}",
                applicable_version=f"v{random.randint(1,4)}.x",
                force_upgrade=random.random() < 0.2,
                description=fake.sentence(),
            )
        )
    session.add_all(firmwares)
    await session.flush()


async def seed_operation_logs(session: AsyncSession, user_ids: list[int] = None):
    if await count_rows(session, OperationLog):
        return

    # Get actual usernames from seeded users for realistic log data
    usernames = []
    if user_ids:
        result = await session.execute(
            select(User.username).where(User.id.in_(user_ids))
        )
        usernames = [r[0] for r in result.all()]
    if not usernames:
        usernames = [f"user{i:03d}" for i in range(1, 31)]

    action_modules = [
        ("登录", "system"), ("登出", "system"),
        ("创建设备", "device"), ("修改设备", "device"), ("删除设备", "device"), ("查看设备", "device"),
        ("创建算法", "algorithm"), ("修改算法", "algorithm"), ("删除算法", "algorithm"),
        ("创建规则", "linkage"), ("修改规则", "linkage"), ("删除规则", "linkage"),
        ("创建用户", "user"), ("修改用户", "user"), ("删除用户", "user"),
        ("导出报表", "system"), ("修改配置", "system"), ("查看日志", "system"),
        ("创建组织", "user"), ("修改组织", "user"),
        ("分配角色", "user"), ("修改角色", "user"),
    ]
    logs = []
    for i in range(120):
        action, module = random.choice(action_modules)
        logs.append(
            OperationLog(
                username=random.choice(usernames),
                action=action,
                ip=fake.ipv4(),
                result=random.choice(["success", "success", "success", "failure"]),
                module=module,
                action_time=random_datetime(datetime(2024, 6, 1), datetime.now()),
            )
        )
    session.add_all(logs)
    await session.flush()


async def seed_clean_records(session: AsyncSession):
    if await count_rows(session, CleanRecord):
        return
    types = ["video", "image", "log"]
    statuses = ["pending", "running", "completed", "failed"]
    records = []
    for i in range(20):
        cutoff = random_datetime(datetime(2023, 1, 1), datetime(2024, 6, 1))
        records.append(
            CleanRecord(
                type=random.choice(types),
                cutoff_time=cutoff,
                status=random.choice(statuses),
                progress=round(random.uniform(0, 100), 2),
                clean_size_bytes=random.randint(1024 * 1024, 100 * 1024 * 1024 * 1024),
            )
        )
    session.add_all(records)
    await session.flush()


async def seed_popup_settings(session: AsyncSession):
    if await count_rows(session, PopupSetting):
        return
    settings = [
        PopupSetting(
            config_json={
                "position": "top-right",
                "duration": 5,
                "sound": True,
                "auto_close": True,
            },
            is_active=True,
        ),
        PopupSetting(
            config_json={
                "position": "bottom-right",
                "duration": 10,
                "sound": False,
                "auto_close": False,
            },
            is_active=False,
        ),
    ]
    session.add_all(settings)
    await session.flush()


async def seed_popup_event_limits(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, PopupEventLimit):
        return
    limits = []
    for did in device_ids[:20]:
        limits.append(
            PopupEventLimit(
                device_id=did,
                time_interval_seconds=random.choice([0, 5, 10, 30, 60]),
                response_mode=random.choice(["immediate", "delay", "ignore"]),
                enabled=random.choice([True, True, False]),
            )
        )
    session.add_all(limits)
    await session.flush()


async def seed_ui_themes(session: AsyncSession):
    if await count_rows(session, UITheme):
        return
    themes = [
        UITheme(name="默认主题", platform="web", theme_color="#409EFF", logo_url="/logo.png", is_active=True),
        UITheme(name="深色主题", platform="web", theme_color="#303133", logo_url="/logo-dark.png", is_active=False),
    ]
    session.add_all(themes)
    await session.flush()


async def seed_microservices(session: AsyncSession):
    if await count_rows(session, Microservice):
        return
    services = [
        Microservice(name="设备服务", service_name="device-service", ip=fake.ipv4_private(), port=8081, cpu_usage=round(random.uniform(10, 60), 2), memory_usage=round(random.uniform(20, 80), 2)),
        Microservice(name="算法服务", service_name="algorithm-service", ip=fake.ipv4_private(), port=8082, cpu_usage=round(random.uniform(15, 70), 2), memory_usage=round(random.uniform(30, 90), 2)),
        Microservice(name="告警服务", service_name="warning-service", ip=fake.ipv4_private(), port=8083, cpu_usage=round(random.uniform(5, 40), 2), memory_usage=round(random.uniform(10, 50), 2)),
        Microservice(name="存储服务", service_name="storage-service", ip=fake.ipv4_private(), port=8084, cpu_usage=round(random.uniform(20, 80), 2), memory_usage=round(random.uniform(40, 95), 2)),
    ]
    session.add_all(services)
    await session.flush()


async def seed_gb28181_devices(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, Gb28181Device):
        return
    gb_devices = []
    for did in random.sample(device_ids, k=min(15, len(device_ids))):
        gb_devices.append(
            Gb28181Device(
                device_id=did,
                manufacturer=random.choice(["海康威视", "大华", "宇视", "天地伟业"]),
                model=random.choice(["DS-2CD", "DH-IPC", "VM"]),
                sip_server_id=f"340200000020000000{random.randint(1,99):02d}",
                sip_device_id=f"340200000013200000{random.randint(1,99):02d}",
                status=random.choice(["active", "active", "inactive"]),
                channels_json=[{"channel_id": i, "name": f"通道{i}"} for i in range(1, random.randint(2, 5))],
            )
        )
    session.add_all(gb_devices)
    await session.flush()


async def seed_onvif_devices(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, OnvifDevice):
        return
    onvif_devices = []
    for did in random.sample(device_ids, k=min(15, len(device_ids))):
        onvif_devices.append(
            OnvifDevice(
                device_id=did,
                manufacturer=random.choice(["Axis", "Bosch", "Sony", "Panasonic"]),
                model=random.choice(["M3027", "FLEXIDOME", "SNC"]),
                ip=fake.ipv4_private(),
                port=random.choice([80, 8080, 2020]),
                status=random.choice(["active", "active", "inactive"]),
                profiles_json=[{"token": f"profile{i}", "name": f"Profile {i}"} for i in range(1, random.randint(2, 4))],
            )
        )
    session.add_all(onvif_devices)
    await session.flush()


async def seed_presets(session: AsyncSession, device_ids: list[int]):
    if await count_rows(session, Preset):
        return
    presets = []
    for did in random.sample(device_ids, k=min(20, len(device_ids))):
        for i in range(random.randint(1, 5)):
            presets.append(
                Preset(
                    device_id=did,
                    name=f"预置位-{i+1}",
                    code=f"P{i+1:02d}",
                    p=round(random.uniform(0, 360), 2),
                    t=round(random.uniform(-90, 90), 2),
                    z=round(random.uniform(1, 30), 2),
                    time_range_json={"start": "00:00", "end": "23:59"} if random.random() < 0.3 else None,
                )
            )
    session.add_all(presets)
    await session.flush()


async def seed_warning_event_archives(session: AsyncSession, device_ids: list[int], org_ids: list[int], region_ids: list[int], algorithm_ids: list[int], event_type_ids: list[int], rule_ids: list[int]):
    if await count_rows(session, WarningEventArchive):
        return
    archives = []
    for i in range(30):
        archives.append(
            WarningEventArchive(
                device_id=random.choice(device_ids) if device_ids else None,
                org_id=random.choice(org_ids) if org_ids else None,
                region_id=random.choice(region_ids) if region_ids else None,
                algorithm_id=random.choice(algorithm_ids) if algorithm_ids else None,
                event_type_id=random.choice(event_type_ids) if event_type_ids else None,
                rule_id=random.choice(rule_ids) if rule_ids else None,
                event_detail=fake.sentence(),
                process_status="resolved",
                is_compliant=True,
                report_time=random_datetime(datetime(2023, 1, 1), datetime(2024, 1, 1)),
                image_url=f"https://example.com/images/archive_{i+1:03d}.jpg",
                video_url=None,
                archived_at=random_datetime(datetime(2024, 1, 1), datetime.now()),
            )
        )
    session.add_all(archives)
    await session.flush()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def seed_all(clear: bool = False):
    async with AsyncSessionLocal() as session:
        if clear:
            print("Truncating all tables...")
            await truncate_all(session)
            print("Tables truncated.")

        # 1. Parent tables first
        org_ids = await seed_organizations(session)
        role_ids = await seed_roles(session)
        menu_ids = await seed_menus(session)
        resource_ids = await seed_resources(session)

        # 2. Users (depend on orgs, roles)
        user_ids = await seed_users(session, org_ids, role_ids)
        await seed_role_permissions(session, role_ids, menu_ids, resource_ids)

        # 3. Regions, platforms, algorithms
        region_ids = await seed_regions(session)
        platform_ids = await seed_access_platforms(session)
        algorithm_ids = await seed_algorithms(session)
        event_type_ids = await seed_event_types(session, algorithm_ids)
        service_ids = await seed_algorithm_services(session)

        # 4. Devices (depend on regions, orgs)
        device_ids = await seed_devices(session, region_ids, org_ids)
        await seed_device_streams(session, device_ids)
        group_ids = await seed_device_groups(session)
        await seed_device_group_memberships(session, group_ids, device_ids)

        # 5. Deployments (depend on algorithms, services, devices)
        deployment_ids = await seed_deployments(session, algorithm_ids, service_ids, device_ids)
        await seed_annotations(session, deployment_ids, device_ids)

        # 6. Linkage rules (depend on algorithms, event_types, devices)
        rule_ids = await seed_linkage_rules(session, algorithm_ids, event_type_ids, device_ids)

        # 7. Warning events (depend on devices, orgs, regions, algorithms, event_types, rules)
        event_ids = await seed_warning_events(session, device_ids, org_ids, region_ids, algorithm_ids, event_type_ids, rule_ids)
        tag_ids = await seed_dispose_tags(session)
        await seed_warning_event_tags(session, event_ids, tag_ids)

        # 8. Push histories (depend on rules, devices, event_types)
        await seed_push_histories(session, rule_ids, device_ids, event_type_ids)

        # 9. Tasks (depend on algorithms, devices)
        await seed_tasks(session, algorithm_ids, device_ids)

        # 10. Video settings (depend on devices)
        await seed_video_settings(session, device_ids)

        # 11. Files (depend on devices)
        await seed_files(session, device_ids)

        # 12. System tables
        await seed_licenses(session)
        await seed_firmwares(session)
        await seed_operation_logs(session, user_ids)
        await seed_clean_records(session)
        await seed_popup_settings(session)
        await seed_popup_event_limits(session, device_ids)
        await seed_ui_themes(session)
        await seed_microservices(session)

        # 13. Device-specific sub-tables
        await seed_gb28181_devices(session, device_ids)
        await seed_onvif_devices(session, device_ids)
        await seed_presets(session, device_ids)

        # 14. Archive
        await seed_warning_event_archives(session, device_ids, org_ids, region_ids, algorithm_ids, event_type_ids, rule_ids)

        await session.commit()
        print("Seed data inserted successfully.")


def main():
    parser = argparse.ArgumentParser(description="Seed database with fake data.")
    parser.add_argument("--clear", action="store_true", help="Truncate tables before seeding")
    args = parser.parse_args()

    asyncio.run(seed_all(clear=args.clear))


if __name__ == "__main__":
    main()

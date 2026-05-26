import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models.warning_event import WarningEvent
from app.models.deployment import Deployment
from app.models.device import Device
from app.models.event_type import EventType
from app.models.algorithm import Algorithm
from app.models.algorithm_service import AlgorithmService


EVENT_TYPES = [
    ("人员聚集", 3, "detection"),
    ("非法入侵", 3, "detection"),
    ("车辆违停", 2, "detection"),
    ("烟火检测", 3, "detection"),
    ("未戴安全帽", 2, "detection"),
    ("区域入侵", 3, "detection"),
    ("打架斗殴", 3, "detection"),
    ("烟雾检测", 2, "detection"),
    ("明火检测", 3, "detection"),
    ("摔倒检测", 2, "detection"),
]

DEPLOYMENT_NAMES = [
    "路口监控部署",
    "园区周界部署",
    "停车场监控部署",
    "仓库安全部署",
    "办公楼大厅部署",
    "工厂车间部署",
    "学校门口部署",
    "医院走廊部署",
    "商场入口部署",
    "小区门禁部署",
]

CAMERA_NAMES = [
    "Camera-001",
    "Camera-002",
    "Camera-003",
    "Camera-004",
    "Camera-005",
    "Camera-006",
    "Camera-007",
    "Camera-008",
    "Camera-009",
    "Camera-010",
    "Camera-011",
    "Camera-012",
    "Camera-013",
    "Camera-014",
    "Camera-015",
    "Camera-016",
    "Camera-017",
    "Camera-018",
    "Camera-019",
    "Camera-020",
]

LOCATIONS = [
    "东门入口",
    "西门出口",
    "南门停车场",
    "北门仓库",
    "A栋大厅",
    "B栋走廊",
    "C栋天台",
    "地下车库A区",
    "地下车库B区",
    "食堂门口",
    "操场北侧",
    "教学楼一楼",
    "住院部大厅",
    "急诊入口",
    "药房窗口",
    "收银台区域",
    "仓库货架区",
    "装卸货平台",
    "消防通道",
    "配电房",
]

STATUSES = ["pending", "processing", "resolved", "ignored"]

IMAGE_URLS = [
    "https://picsum.photos/400/300?random=1",
    "https://picsum.photos/400/300?random=2",
    "https://picsum.photos/400/300?random=3",
    "https://picsum.photos/400/300?random=4",
    "https://picsum.photos/400/300?random=5",
]


async def seed_event_types(db: AsyncSession):
    result = await db.execute(select(EventType).where(EventType.deleted_at.is_(None)))
    existing = result.scalars().all()
    if existing:
        print(f"Event types already exist ({len(existing)}), skipping.")
        return existing

    items = []
    for name, severity, category in EVENT_TYPES:
        item = EventType(name=name, severity=severity, category=category)
        db.add(item)
        items.append(item)
    await db.commit()
    for item in items:
        await db.refresh(item)
    print(f"Created {len(items)} event types.")
    return items


async def seed_algorithms(db: AsyncSession):
    result = await db.execute(select(Algorithm).where(Algorithm.deleted_at.is_(None)))
    existing = result.scalars().all()
    if existing:
        print(f"Algorithms already exist ({len(existing)}), skipping.")
        return existing

    items = []
    for i, (name, _, _) in enumerate(EVENT_TYPES):
        item = Algorithm(
            name=f"{name}算法",
            type="detection",
            description=f"用于检测{name}的AI算法",
            business_category="security",
        )
        db.add(item)
        items.append(item)
    await db.commit()
    for item in items:
        await db.refresh(item)
    print(f"Created {len(items)} algorithms.")
    return items


async def seed_algorithm_services(db: AsyncSession):
    result = await db.execute(select(AlgorithmService).where(AlgorithmService.deleted_at.is_(None)))
    existing = result.scalars().all()
    if existing:
        print(f"Algorithm services already exist ({len(existing)}), skipping.")
        return existing

    items = []
    for i in range(3):
        item = AlgorithmService(
            service_id=f"svc-{i+1:03d}",
            service_name=f"算法服务节点-{i+1}",
            service_code=f"service-{i+1}",
            service_ip=f"192.168.1.{10+i}",
            service_port=8080 + i,
            annotation_ip=f"192.168.1.{20+i}",
            annotation_port=9090 + i,
            status="active",
        )
        db.add(item)
        items.append(item)
    await db.commit()
    for item in items:
        await db.refresh(item)
    print(f"Created {len(items)} algorithm services.")
    return items


async def seed_devices(db: AsyncSession):
    result = await db.execute(select(Device).where(Device.deleted_at.is_(None)))
    existing = result.scalars().all()
    if existing:
        print(f"Devices already exist ({len(existing)}), skipping.")
        return existing

    items = []
    for i, name in enumerate(CAMERA_NAMES):
        item = Device(
            device_code=f"DEV-{i+1:04d}",
            name=name,
            status=random.choice(["active", "active", "active", "inactive"]),
            access_type="direct",
            device_type="camera",
            longitude=random.uniform(116.3, 116.5),
            latitude=random.uniform(39.9, 40.0),
            memory_usage=random.uniform(30.0, 80.0),
            disk_size=random.randint(1000000000, 5000000000),
            disk_usage=random.uniform(20.0, 70.0),
            remark=f"位于{LOCATIONS[i % len(LOCATIONS)]}的监控设备",
        )
        db.add(item)
        items.append(item)
    await db.commit()
    for item in items:
        await db.refresh(item)
    print(f"Created {len(items)} devices.")
    return items


async def seed_deployments(db: AsyncSession, algorithms, services):
    result = await db.execute(select(Deployment).where(Deployment.deleted_at.is_(None)))
    existing = result.scalars().all()
    if existing:
        print(f"Deployments already exist ({len(existing)}), skipping.")
        return existing

    items = []
    for i, name in enumerate(DEPLOYMENT_NAMES):
        algo = algorithms[i % len(algorithms)]
        svc = services[i % len(services)]
        item = Deployment(
            name=name,
            algorithm_id=algo.id,
            service_id=svc.id,
            status=random.choice(["active", "active", "inactive"]),
            algorithm_status=random.choice(["running", "running", "stopped", "error"]),
            deployed_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
        )
        db.add(item)
        items.append(item)
    await db.commit()
    for item in items:
        await db.refresh(item)
    print(f"Created {len(items)} deployments.")
    return items


async def seed_warning_events(db: AsyncSession, devices, event_types):
    result = await db.execute(select(WarningEvent).where(WarningEvent.deleted_at.is_(None)))
    existing = result.scalars().all()
    if existing:
        print(f"Warning events already exist ({len(existing)}), skipping.")
        return existing

    items = []
    now = datetime.utcnow()
    for i in range(200):
        device = random.choice(devices)
        event_type = random.choice(event_types)
        report_time = now - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        item = WarningEvent(
            device_id=device.id,
            event_type_id=event_type.id,
            algorithm_id=event_type.algorithm_id,
            event_detail=random.choice(LOCATIONS),
            process_status=random.choice(STATUSES),
            report_time=report_time,
            image_url=random.choice(IMAGE_URLS),
        )
        db.add(item)
        items.append(item)

    await db.commit()
    for item in items:
        await db.refresh(item)
    print(f"Created {len(items)} warning events.")
    return items


async def main():
    async with AsyncSessionLocal() as db:
        event_types = await seed_event_types(db)
        algorithms = await seed_algorithms(db)
        services = await seed_algorithm_services(db)
        devices = await seed_devices(db)
        await seed_deployments(db, algorithms, services)
        await seed_warning_events(db, devices, event_types)
    print("Dashboard seed completed.")


if __name__ == "__main__":
    import sys
    sys.path.insert(0, r"E:\python\code\console\ai-console\backend")
    from sqlalchemy import select
    asyncio.run(main())

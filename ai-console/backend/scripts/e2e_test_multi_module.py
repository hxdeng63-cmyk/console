"""
End-to-end test for multi-module parallel detection.

Requires:
- Backend running on http://127.0.0.1:10088
- PostgreSQL on port 5434
- A test device with a local video file registered as a data_source

Usage:
    cd /home/daxiong/code/console/ai-console/backend
    DATABASE_URL="postgresql+asyncpg://postgres:PASSWORD@localhost:5434/ai_console" \
        python scripts/e2e_test_multi_module.py --device-id <id>
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time
from pathlib import Path

import requests
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.models.algorithm import Algorithm
from app.models.warning_event import WarningEvent
from app.models.deployment import Deployment
from app.models.event_type import EventType
from app.models.file import File

BACKEND_URL = "http://127.0.0.1:10088"
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5434/ai_console",
)


def get_db_session() -> tuple[async_sessionmaker, AsyncEngine]:
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return session_factory, engine


async def get_event_type_ids(db: AsyncSession) -> dict[str, int]:
    result = await db.execute(
        select(EventType.name, EventType.id)
        .join(Algorithm, EventType.algorithm_id == Algorithm.id)
        .where(Algorithm.name == "traffic", EventType.deleted_at.is_(None))
    )
    return {name: eid for name, eid in result.all()}


async def create_video_setting(device_id: int) -> int:
    """Create or update a VideoSetting with all 7 traffic event types for the device."""
    session_factory, _ = get_db_session()
    async with session_factory() as db:
        event_type_map = await get_event_type_ids(db)

    event_type_ids = sorted(event_type_map.values())
    payload = {
        "org_id": 8,
        "event_types": event_type_ids,
        "device_ids": [device_id],
        "record_duration_seconds": 30,
        "status": True,
    }

    # Try create first; if org already has setting, update it.
    resp = requests.post(f"{BACKEND_URL}/api/v1/video-settings", json=payload, timeout=10)
    if resp.status_code == 400 and "该公司已配置录像设置" in resp.text:
        # List settings to find id
        list_resp = requests.get(
            f"{BACKEND_URL}/api/v1/video-settings", params={"org_id": 8}, timeout=10
        )
        list_resp.raise_for_status()
        data = list_resp.json()
        for item in data.get("items", []):
            setting_id = item["id"]
            put_resp = requests.put(
                f"{BACKEND_URL}/api/v1/video-settings/{setting_id}", json=payload, timeout=10
            )
            put_resp.raise_for_status()
            return setting_id
    resp.raise_for_status()
    return resp.json()["id"]


async def wait_for_deployments(db: AsyncSession, device_id: int, expected_modules: set[str], timeout: int = 120) -> list[Deployment]:
    """Wait until active deployments for the device match expected modules."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = await db.execute(
            select(Deployment).where(
                Deployment.device_id == device_id,
                Deployment.deleted_at.is_(None),
            )
        )
        deployments = list(result.scalars().all())
        modules = {d.module_name for d in deployments if d.module_name}
        if modules == expected_modules and all(d.algorithm_status == "running" for d in deployments):
            return deployments
        await asyncio.sleep(2)
    raise TimeoutError(f"Deployments did not reach expected state within {timeout}s")


async def wait_for_events(
    db: AsyncSession,
    device_id: int,
    event_type_names: list[str],
    timeout: int = 180,
) -> dict[str, list[WarningEvent]]:
    """Wait until at least one event with media URLs exists for each event type."""
    deadline = time.time() + timeout
    event_type_map = await get_event_type_ids(db)
    found: dict[str, list[WarningEvent]] = {name: [] for name in event_type_names}
    while time.time() < deadline:
        for name in list(found.keys()):
            if found[name]:
                continue
            et_id = event_type_map.get(name)
            if not et_id:
                continue
            result = await db.execute(
                select(WarningEvent).where(
                    WarningEvent.device_id == device_id,
                    WarningEvent.event_type_id == et_id,
                    WarningEvent.image_url.isnot(None),
                    WarningEvent.video_url.isnot(None),
                    WarningEvent.deleted_at.is_(None),
                )
            )
            events = list(result.scalars().all())
            if events:
                found[name] = events
        if all(found.values()):
            return found
        await asyncio.sleep(5)
    return found


async def verify_files(db: AsyncSession, events: list[WarningEvent]) -> int:
    """Return count of events that have associated File records."""
    count = 0
    for event in events:
        result = await db.execute(
            select(File).where(
                File.warning_event_id == event.id,
                File.deleted_at.is_(None),
            )
        )
        files = list(result.scalars().all())
        if files:
            count += 1
    return count


async def test_media_urls(events: list[WarningEvent]) -> tuple[int, int]:
    """Return (image_ok, video_ok) counts."""
    image_ok = 0
    video_ok = 0
    for event in events:
        if event.image_url:
            resp = requests.get(f"{BACKEND_URL}{event.image_url}", timeout=10)
            if resp.status_code == 200:
                image_ok += 1
        if event.video_url:
            resp = requests.get(f"{BACKEND_URL}{event.video_url}", timeout=10)
            if resp.status_code == 200:
                video_ok += 1
    return image_ok, video_ok


async def test_restart_isolation(db: AsyncSession, device_id: int) -> dict:
    result = await db.execute(
        select(Deployment).where(
            Deployment.device_id == device_id,
            Deployment.deleted_at.is_(None),
        )
    )
    deployments = list(result.scalars().all())
    if not deployments:
        return {"error": "no deployments to test"}

    target = deployments[0]
    original_pid = target.pid
    if not original_pid:
        return {"error": f"deployment {target.id} has no pid"}

    # Kill the process
    try:
        os.kill(original_pid, 9)
    except ProcessLookupError:
        pass

    # Wait for restart or error status
    deadline = time.time() + 20
    restarted = False
    while time.time() < deadline:
        await db.refresh(target)
        if target.pid and target.pid != original_pid and target.algorithm_status == "running":
            restarted = True
            break
        await asyncio.sleep(1)

    return {
        "deployment_id": target.id,
        "module_name": target.module_name,
        "original_pid": original_pid,
        "new_pid": target.pid,
        "status": target.algorithm_status,
        "restarted": restarted,
    }


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--device-id", type=int, required=True, help="Test device ID")
    args = parser.parse_args()

    print(f"Using device_id={args.device_id}")
    print("Creating VideoSetting with all 7 traffic event types...")
    setting_id = await create_video_setting(args.device_id)
    print(f"VideoSetting id={setting_id}")

    session_factory, engine = get_db_session()
    async with session_factory() as db:
        expected_modules = {
            "traffic_jam",
            "vehicle_counting",
            "reverse_detection",
            "pedestrian_intrusion",
            "accident_detection",
            "vest_detection",
        }
        print("Waiting for deployments to become running...")
        deployments = await wait_for_deployments(db, args.device_id, expected_modules)
        print(f"Deployments: {len(deployments)}")
        for d in deployments:
            print(f"  {d.module_name}: pid={d.pid}, status={d.algorithm_status}")

        # Verify deduplication: vehicle_counting should appear once even for anomaly+flow
        vehicle_count = sum(1 for d in deployments if d.module_name == "vehicle_counting")
        print(f"vehicle_counting deployments: {vehicle_count} (expected 1)")

        print("Waiting for events from each module (this may take a few minutes)...")
        event_names = ["jam", "anomaly", "flow", "reverse", "pedestrian", "accident", "vest"]
        found_events = await wait_for_events(db, args.device_id, event_names, timeout=180)

        total_events = 0
        for name, events in found_events.items():
            print(f"  {name}: {len(events)} events")
            total_events += len(events)

        # Verify files and URLs for the first event of each type
        all_events = [e for events in found_events.values() for e in events]
        file_count = await verify_files(db, all_events)
        image_ok, video_ok = await test_media_urls(all_events)
        print(f"Events with File records: {file_count}/{len(all_events)}")
        print(f"Image URLs returning 200: {image_ok}/{len(all_events)}")
        print(f"Video URLs returning 200: {video_ok}/{len(all_events)}")

        print("Testing crash isolation (kill one module)...")
        restart_result = await test_restart_isolation(db, args.device_id)
        print(f"  restart result: {restart_result}")

    await engine.dispose()
    print("E2E test completed")


if __name__ == "__main__":
    asyncio.run(main())

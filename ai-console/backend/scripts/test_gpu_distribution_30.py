"""Stress-test ProcessMonitor GPU distribution with 30 concurrent starts."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.process_monitor import ProcessMonitor

_VIDEO = "docs/monitoring/南区-设备1.mp4"
_MODULE = "vehicle_counting"


async def start_one(monitor, dep_id):
    try:
        result = await monitor.start(
            module_name=_MODULE,
            video_path=_VIDEO,
            deployment_id=dep_id,
            stream_id=f"test_{dep_id}",
        )
        return dep_id, result["pid"], None
    except Exception as exc:
        return dep_id, None, exc


async def main():
    monitor = ProcessMonitor()
    ids = list(range(999101, 999131))
    results = await asyncio.gather(*[start_one(monitor, i) for i in ids])

    await asyncio.sleep(3)

    counts = {}
    for dep_id, pid, err in results:
        if err:
            print(f"dep {dep_id} failed: {err}")
            continue
        env_path = f"/proc/{pid}/environ"
        val = "(exited)"
        if os.path.exists(env_path):
            raw = open(env_path, "rb").read().decode("utf-8", errors="ignore")
            val = (
                raw.split("CUDA_VISIBLE_DEVICES=")[1].split("\0")[0]
                if "CUDA_VISIBLE_DEVICES=" in raw
                else "(not set)"
            )
        counts[val] = counts.get(val, 0) + 1
        print(f"dep {dep_id} pid={pid} CUDA={val}")

    print("\ndistribution:", counts)

    for dep_id, _, _ in results:
        try:
            await monitor.stop(dep_id)
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())

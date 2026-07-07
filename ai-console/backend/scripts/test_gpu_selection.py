"""Test ProcessMonitor GPU distribution locally."""

import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.process_monitor import ProcessMonitor

# Per migration: monitoring fallback files moved to data/monitoring/
_VIDEO = "data/monitoring/device_51.mp4"
_MODULE = "vehicle_counting"


async def main():
    monitor = ProcessMonitor()
    pids = []
    for i in range(4):
        dep_id = 999001 + i
        try:
            result = await monitor.start(
                module_name=_MODULE,
                video_path=_VIDEO,
                deployment_id=dep_id,
                stream_id=f"test_{dep_id}",
            )
            pids.append((dep_id, result["pid"]))
            print(f"deployment {dep_id} pid={result['pid']}")
        except Exception as exc:
            print(f"deployment {dep_id} failed: {exc}")

    await asyncio.sleep(2)

    for dep_id, pid in pids:
        env_path = f"/proc/{pid}/environ"
        if os.path.exists(env_path):
            val = (
                open(env_path, "rb")
                .read()
                .decode("utf-8", errors="ignore")
                .split("CUDA_VISIBLE_DEVICES=")[1]
                .split("\0")[0]
                if "CUDA_VISIBLE_DEVICES=" in open(env_path, "rb").read().decode("utf-8", errors="ignore")
                else "(not set)"
            )
            print(f"dep {dep_id} CUDA_VISIBLE_DEVICES={val}")

    # stop them
    for dep_id, _ in pids:
        try:
            await monitor.stop(dep_id)
        except Exception as exc:
            print(f"stop {dep_id} failed: {exc}")


if __name__ == "__main__":
    asyncio.run(main())

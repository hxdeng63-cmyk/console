#!/usr/bin/env python3
"""Start all active deployments concurrently via the backend REST API."""

import asyncio
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

BASE = "http://127.0.0.1:10088/api/v1"


def fetch_deployments() -> list[dict]:
    resp = requests.get(f"{BASE}/deployments", params={"page": 1, "page_size": 100}, timeout=30)
    resp.raise_for_status()
    return resp.json()["items"]


def start_deployment(dep: dict) -> dict:
    payload = {
        "module_name": dep["module_name"],
        "video_path": "auto",
        "stream_map": dep.get("config_json", {}).get("stream_map"),
        "config": dep.get("config_json", {}).get("module_config") or {},
    }
    resp = requests.post(
        f"{BASE}/deployments/{dep['id']}/start",
        json=payload,
        timeout=30,
    )
    try:
        resp.raise_for_status()
    except Exception as exc:
        print(f"start failed for deployment {dep['id']}: {exc} - {resp.text}")
        raise
    return resp.json()


def poll_task(task_id: str, deployment_id: int) -> dict:
    while True:
        resp = requests.get(f"{BASE}/deployments/{deployment_id}/start/status/{task_id}", timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") in ("completed", "failed"):
            return data
        time.sleep(0.5)


async def main() -> int:
    deps = fetch_deployments()
    print(f"Found {len(deps)} deployments")

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=30) as pool:
        start_results = await asyncio.gather(
            *[loop.run_in_executor(pool, start_deployment, dep) for dep in deps],
            return_exceptions=True,
        )

    task_map = []
    for dep, result in zip(deps, start_results):
        if isinstance(result, Exception):
            print(f"deployment {dep['id']} start request failed: {result}")
            continue
        print(f"deployment {dep['id']} -> task {result.get('task_id')} ({result.get('status')})")
        task_map.append((dep["id"], result["task_id"]))

    print(f"Launched {len(task_map)} start tasks; waiting for them to complete...")
    with ThreadPoolExecutor(max_workers=30) as pool:
        final_results = await asyncio.gather(
            *[loop.run_in_executor(pool, poll_task, tid, did) for did, tid in task_map],
            return_exceptions=True,
        )

    ok = 0
    fail = 0
    for (did, tid), result in zip(task_map, final_results):
        if isinstance(result, Exception):
            print(f"deployment {did} task {tid} polling error: {result}")
            fail += 1
            continue
        status = result.get("status")
        if status == "completed":
            ok += 1
        else:
            print(f"deployment {did} task {tid} status={status} error={result.get('error')}")
            fail += 1

    print(f"Done: ok={ok}, failed={fail}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

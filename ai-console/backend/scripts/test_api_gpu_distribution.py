"""Start all 30 deployments via API concurrently and inspect GPU env of running processes."""

import json
import subprocess
import time
import os

BASE = "http://127.0.0.1:10088/api/v1"

# get deployment ids
deps = json.loads(subprocess.check_output(
    ["curl", "-sS", f"{BASE}/deployments?page=1&page_size=100"]
).decode())["items"]
ids = [d["id"] for d in deps]
print(f"starting {len(ids)} deployments")

# fire all start requests concurrently
procs = []
for d in deps:
    payload = json.dumps({"module_name": d["module_name"], "video_path": "auto", "config": {}})
    p = subprocess.Popen(
        ["curl", "-sS", "-X", "POST", f"{BASE}/deployments/{d['id']}/start",
         "-H", "Content-Type: application/json", "-d", payload],
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
    )
    procs.append((d["id"], p))

for did, p in procs:
    p.wait()

print("all start requests sent, waiting 5s...")
time.sleep(5)

# count running and inspect env
running_envs = {}
for d in json.loads(subprocess.check_output(
    ["curl", "-sS", f"{BASE}/deployments?page=1&page_size=100"]
).decode())["items"]:
    if d["algorithm_status"] == "running" and d.get("pid"):
        pid = d["pid"]
        env_path = f"/proc/{pid}/environ"
        if os.path.exists(env_path):
            raw = open(env_path, "rb").read().decode("utf-8", errors="ignore")
            val = (
                raw.split("CUDA_VISIBLE_DEVICES=")[1].split("\0")[0]
                if "CUDA_VISIBLE_DEVICES=" in raw
                else "unset"
            )
            running_envs[val] = running_envs.get(val, 0) + 1

print("running env distribution:", running_envs)

# stop running
for d in json.loads(subprocess.check_output(
    ["curl", "-sS", f"{BASE}/deployments?page=1&page_size=100"]
).decode())["items"]:
    if d["algorithm_status"] == "running":
        subprocess.run(["curl", "-sS", "-X", "POST", f"{BASE}/deployments/{d['id']}/stop"], capture_output=True)

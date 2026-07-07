#!/usr/bin/env python3
"""Reorganize data/photo-videos/ to new per-detection folder structure.

Per .omc/specs/deep-interview-photo-videos-archive.md (option B ingest):
- 每个 detection 一个文件夹: data/photo-videos/{event}/{event}_{device_name}_{ts}_{uuid8}/
- 内含 image.jpg + video.mp4

历史数据 (3889 + 30 files) 按相同规则重组。

Usage:
    python scripts/reorganize_photo_videos.py --dry-run    # 只打印
    python scripts/reorganize_photo_videos.py             # 实际迁移
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path("/home/daxiong/code/console")
DATA_ROOT = PROJECT_ROOT / "data"
PHOTO_VIDEOS = DATA_ROOT / "photo-videos"

# Legacy algorithm → new event name
EVENT_NAME_MAP = {
    "traffic_jam": "jam",
    "vehicle_counting": "flow",
    "reverse_detection": "reverse",
    "pedestrian_intrusion": "pedestrian",
    "accident_detection": "accident",
    "vest_detection": "vest",
}

# 文件名 event token (form 2b/2c 用)
FILENAME_EVENT_TOKENS = "pedestrian|accident|vest|jam|anomaly|flow|reverse"

# 设备 id → device name 映射 (从 DB; 这里硬编码已知 5 个 device)
DEVICE_NAME_MAP = {
    "51": "南区-设备1",
    "52": "南区-设备2",
    "53": "南区-设备3",
    "54": "北区-设备1",
    "55": "西区-设备1",
}

# detection_id namespace
_DETECTION_NS = uuid.UUID("a3b8c5d2-1e9f-4a7b-8c6d-2e1f0a9b8c7d")


def make_detection_id(
    event_name: str, device_name: str, timestamp: str, salt: str = ""
) -> str:
    seed = f"{event_name}|{device_name}|{timestamp}|{salt}"
    u = uuid.uuid5(_DETECTION_NS, seed)
    return f"{event_name}_{device_name}_{timestamp}_{u.hex[:8]}"


def is_already_migrated(path: Path) -> bool:
    """判断是否已经重组过 (image.jpg + video.mp4 + .gitkeep 都在)."""
    if not path.is_dir():
        return False
    files = {f.name for f in path.iterdir() if f.is_file() and f.name != ".gitkeep"}
    return files == {"image.jpg", "video.mp4"}


def device_id_from_rel(rel: Path) -> str:
    """从 PHOTO_VIDEOS 相对路径推断 device_id (字符串)。
    rel 形如 {event}/{N}/... 或 {event}/{N}_{event_legacy}/... 或 {event}/camera_*/...
    parts[1] 是 device_id 或 N_event_legacy 或 camera_*
    """
    parts = rel.parts
    if len(parts) < 2:
        return ""
    sub = parts[1]
    # 纯数字
    if sub.isdigit():
        return sub
    # {N}_{event_legacy} → 取 N
    m = re.match(r"^(\d+)_", sub)
    if m:
        return m.group(1)
    # camera_xxx → 不确定 device_id (返回空 → 用 unknown)
    return ""


def event_from_filename(filename: str) -> str | None:
    """从文件名提取 event (form 2b/2c 模式: pedestrian_147_1782910592.jpg)."""
    m = re.match(rf"^({FILENAME_EVENT_TOKENS})_", filename)
    if m:
        return m.group(1)
    return None


def timestamp_from_filename(filename: str) -> str:
    """从文件名提取 timestamp (form 2b/2c: pedestrian_147_1782910592.jpg → 1782910592)."""
    m = re.match(rf"^({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.", filename)
    if m:
        return m.group(3)
    return ""


def derive_target_path(src_file: Path) -> Path | None:
    """从 src_file 推断新结构的 save_path."""
    # src_file: data/photo-videos/{event}/{N}/.../file.ext
    try:
        rel = src_file.relative_to(PHOTO_VIDEOS)
    except ValueError:
        return None
    parts = rel.parts  # e.g. ('pedestrian', '53', '20260626', 'pedestrian_147_1782910592.jpg')

    if len(parts) < 2:
        return None

    event_name = parts[0]
    device_id = device_id_from_rel(rel)
    device_name = DEVICE_NAME_MAP.get(device_id, f"dev_{device_id}" if device_id else "unknown")

    # 提取 timestamp
    timestamp = ""
    if len(parts) >= 4:
        # 形如 event/N/date/file.ext → timestamp 从 date 取 (20260626)
        if re.match(r"^\d{8}$", parts[2]):
            timestamp = parts[2]
        else:
            # 形如 event/N_event_legacy/date/file.ext → date 同样
            timestamp = parts[2]
        # 文件名里如果有 unix timestamp, 优先用 (更精确)
        ts_from_file = timestamp_from_filename(src_file.name)
        if ts_from_file:
            timestamp = ts_from_file
    elif len(parts) == 3:
        # 形如 event/N/file.ext (form 5) → 用文件 mtime
        timestamp = src_file.stat().st_mtime if src_file.exists() else ""
        timestamp = str(int(float(timestamp))) if timestamp else "00000000"
    else:
        return None

    # 文件 kind: .jpg → image, .mp4 → video
    ext = src_file.suffix.lower().lstrip(".")
    if ext == "jpg":
        file_kind = "image"
    elif ext == "mp4":
        file_kind = "video"
    else:
        return None

    # salt 用 parent dir + basename stem (去掉 .jpg/.mp4), 保证 image+video 同 detection
    salt = f"{src_file.parent.relative_to(DATA_ROOT)}/{src_file.stem}"

    det_id = make_detection_id(event_name, device_name, timestamp, salt)
    return PHOTO_VIDEOS / event_name / det_id / f"{file_kind}.{ext}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--event", help="只处理指定事件 (e.g. pedestrian)")
    args = parser.parse_args()

    if not PHOTO_VIDEOS.exists():
        print(f"PHOTO_VIDEOS 不存在: {PHOTO_VIDEOS}")
        return 1

    moves = []
    for src_file in PHOTO_VIDEOS.rglob("*"):
        if not src_file.is_file():
            continue
        if src_file.name == ".gitkeep":
            continue
        target = derive_target_path(src_file)
        if target is None:
            print(f"  SKIP (无法推断): {src_file.relative_to(DATA_ROOT)}")
            continue
        if src_file == target:
            continue  # 已经在新位置
        moves.append((src_file, target))

    print(f"将移动 {len(moves)} 个文件:")
    for src, dst in moves[:5]:
        print(f"  {src.relative_to(DATA_ROOT)} → {dst.relative_to(DATA_ROOT)}")
    if len(moves) > 5:
        print(f"  ... (还有 {len(moves) - 5} 个)")

    if args.dry_run:
        print("\nDRY-RUN: 没实际移动")
        return 0

    confirm = input(f"\n确认移动 {len(moves)} 个文件? [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("取消")
        return 1

    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            print(f"  跳过 (目标已存在): {dst.relative_to(DATA_ROOT)}")
            continue
        shutil.move(str(src), str(dst))

    # 清理空的旧目录
    cleaned = 0
    for d in sorted(PHOTO_VIDEOS.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            cleaned += 1
    print(f"\n迁移完成. 移动 {len(moves)} 个文件, 清理 {cleaned} 个空目录.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
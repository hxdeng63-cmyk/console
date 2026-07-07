#!/usr/bin/env python3
"""Consolidate detection dirs: image.jpg + video.mp4 from same detection share folder.

Problem: 之前 reorganize 用 salt={full_relative_path} (含扩展名), 导致 image 和 video
生成不同 detection_id. 现在用 salt={parent}/{stem} (无扩展名) 重算并合并。

Usage:
    python scripts/consolidate_detections.py --dry-run    # 只打印
    python scripts/consolidate_detections.py             # 实际合并
"""
from __future__ import annotations

import argparse
import shutil
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path("/home/daxiong/code/console")
DATA_ROOT = PROJECT_ROOT / "data"
PHOTO_VIDEOS = DATA_ROOT / "photo-videos"

DEVICE_NAME_MAP = {
    "51": "南区-设备1",
    "52": "南区-设备2",
    "53": "南区-设备3",
    "54": "北区-设备1",
    "55": "西区-设备1",
}

_DETECTION_NS = uuid.UUID("a3b8c5d2-1e9f-4a7b-8c6d-2e1f0a9b8c7d")


def make_detection_id(event_name, device_name, timestamp, salt=""):
    seed = f"{event_name}|{device_name}|{timestamp}|{salt}"
    u = uuid.uuid5(_DETECTION_NS, seed)
    return f"{event_name}_{device_name}_{timestamp}_{u.hex[:8]}"


def derive_event_name_and_metadata(file_path: Path):
    """从当前 file_path 反推 event_name + device_name + timestamp.

    file_path 形如 photo-videos/{event}/{old_det_id}/{image.jpg|video.mp4}
    但 {old_det_id} 包含 event_name + device_name + timestamp 信息 (格式: {event}_{device}_{ts}_{uuid8})

    Returns: (event_name, device_name, timestamp, salt)
    """
    rel = file_path.relative_to(PHOTO_VIDEOS)
    parts = rel.parts  # ('{event}', '{old_det_id}', '{image.jpg|video.mp4}')
    event_name = parts[0]
    old_det_id = parts[1]
    # old_det_id 格式: {event}_{device}_{ts}_{uuid8}
    # 拆分: parts[0]=event, parts[1]=device, parts[2]=ts, parts[3]=uuid8
    id_parts = old_det_id.split("_")
    if len(id_parts) >= 4:
        # 设备名可能含下划线, 用 uuid8 (8 字符) 定位
        uuid8 = id_parts[-1]
        ts = id_parts[-2]
        device_name = "_".join(id_parts[1:-2])
    else:
        device_name = "unknown"
        ts = "00000000"
    salt = f"{file_path.parent.relative_to(DATA_ROOT)}/{file_path.stem}"
    return event_name, device_name, ts, salt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    moves = []  # (src, dst)
    for event_dir in PHOTO_VIDEOS.iterdir():
        if not event_dir.is_dir():
            continue
        for det_dir in event_dir.iterdir():
            if not det_dir.is_dir():
                continue
            for f in det_dir.iterdir():
                if not f.is_file() or f.name == ".gitkeep":
                    continue
                # 跳过已经在新结构的 (有 image.jpg + video.mp4)
                if det_dir.joinpath("image.jpg").exists() and det_dir.joinpath("video.mp4").exists():
                    continue

                # 从旧 det_id 提取 metadata, 用新 salt 算正确 det_id
                event_name, device_name, ts, salt = derive_event_name_and_metadata(f)
                if event_name not in ["accident", "anomaly", "flow", "jam", "pedestrian", "reverse", "vest"]:
                    continue  # 跳过非事件目录
                if not ts.isdigit():
                    continue
                correct_det_id = make_detection_id(event_name, device_name, ts, salt)
                ext = f.suffix
                correct_dst = event_dir / correct_det_id / f.name
                if f.parent == correct_dst.parent:
                    # 已经在正确位置
                    if f.name == "image.jpg" and not (correct_dst.parent / "video.mp4").exists():
                        continue  # 单文件检测 (没有 video), 保留
                    continue
                moves.append((f, correct_dst))

    print(f"将移动 {len(moves)} 个文件:")
    for src, dst in moves[:5]:
        print(f"  {src.relative_to(DATA_ROOT)} → {dst.relative_to(DATA_ROOT)}")
    if len(moves) > 5:
        print(f"  ... (还有 {len(moves) - 5} 个)")

    if args.dry_run:
        print("\nDRY-RUN")
        return 0

    confirm = input(f"\n确认移动 {len(moves)} 个文件? [yes/no]: ")
    if confirm.strip().lower() != "yes":
        return 1

    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            continue  # 已存在 (image.jpg 已在正确位置, video.mp4 也对)
        shutil.move(str(src), str(dst))

    # 清理空的旧 det_id dirs
    cleaned = 0
    for d in sorted(PHOTO_VIDEOS.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            cleaned += 1
    print(f"完成. 移动 {len(moves)} 个文件, 清理 {cleaned} 个空目录.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
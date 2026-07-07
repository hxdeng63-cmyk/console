#!/usr/bin/env python3
"""Consolidate: image.jpg + video.mp4 of same detection → same folder.

反推逻辑: 当前每个 dir 形如 {event}_{device_name}_{ts}_{uuid8}.
image 和 video 来自同一个 detection 时, 它们的 parent dir 有相同的 (event, device_name, ts) 前缀,
只是 uuid8 不同 (前次 bad migration 的 salt bug).

按 (event, device_name, ts) 配对 → 合并到新 det_id dir.
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import uuid
from collections import defaultdict
from pathlib import Path

PROJECT_ROOT = Path("/home/daxiong/code/console")
DATA_ROOT = PROJECT_ROOT / "data"
PHOTO_VIDEOS = DATA_ROOT / "photo-videos"

_VALID_EVENTS = {"accident", "anomaly", "flow", "jam", "pedestrian", "reverse", "vest"}

_DETECTION_NS = uuid.UUID("a3b8c5d2-1e9f-4a7b-8c6d-2e1f0a9b8c7d")


def make_detection_id(event_name, device_name, ts, salt):
    seed = f"{event_name}|{device_name}|{ts}|{salt}"
    u = uuid.uuid5(_DETECTION_NS, seed)
    return f"{event_name}_{device_name}_{ts}_{u.hex[:8]}"


def parse_parent_dir(parent_name: str) -> tuple | None:
    """{event}_{device_name}_{ts}_{uuid8} → (event, device_name, ts, uuid8)"""
    m = re.match(r"^([a-z]+)_(.+?)_(\d+)_([0-9a-f]{8})$", parent_name)
    if not m:
        return None
    event, device, ts, uuid8 = m.groups()
    if event not in _VALID_EVENTS:
        return None
    return event, device, ts, uuid8


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    # 1. 收集所有文件, 按 (event, device_name) 分组 + 记录 mtime
    by_group: dict[tuple, list[tuple[Path, str, int]]] = defaultdict(list)
    # group_key = (event, device_name) → [(file_path, kind, mtime), ...]
    skipped_already = 0
    skipped_unparseable: list[Path] = []

    for src_file in PHOTO_VIDEOS.rglob("*"):
        if not src_file.is_file() or src_file.name == ".gitkeep":
            continue
        parent = src_file.parent
        if (parent / "image.jpg").exists() and (parent / "video.mp4").exists():
            skipped_already += 1
            continue

        parsed = parse_parent_dir(parent.name)
        if parsed is None:
            skipped_unparseable.append(src_file)
            continue

        event, device, ts, uuid8 = parsed
        kind = "image" if src_file.suffix.lower() == ".jpg" else "video"
        by_group[(event, device)].append((src_file, kind, int(ts)))

    if skipped_already:
        print(f"跳过已正确 ({skipped_already} 个)")

    if skipped_unparseable:
        print(f"未解析的 {len(skipped_unparseable)} 个文件:")
        for f in skipped_unparseable[:5]:
            print(f"  {f.relative_to(DATA_ROOT)}")
        if len(skipped_unparseable) > 5:
            print(f"  ... (还有 {len(skipped_unparseable) - 5} 个)")

    # 2. 每个 (event, device) 组内: 按 ts 排序, greedy 配对 image↔video (ts 最近)
    # 容忍: form 5 image mtime 晚于 video 0-600s (ffmpeg 提取延迟)
    moves: list[tuple[Path, Path]] = []
    for (event, device), files in by_group.items():
        # 按 mtime 排序
        files.sort(key=lambda x: x[2])
        # greedy: 对每个 image 找最近的 video (±600s)
        used = set()
        images = [(f, k, t) for f, k, t in files if k == "image"]
        videos = [(f, k, t) for f, k, t in files if k == "video"]

        for img_path, _, img_ts in images:
            if img_path in used:
                continue
            # 找最近的未用 video
            best_vid = None
            best_diff = 10**9
            for vid_path, _, vid_ts in videos:
                if vid_path in used:
                    continue
                diff = abs(img_ts - vid_ts)
                if diff < best_diff:
                    best_diff = diff
                    best_vid = vid_path
            if best_vid is not None and best_diff <= 600:
                used.add(img_path)
                used.add(best_vid)
                # 用较早的 ts 作为 det ts
                ts = str(min(img_ts, best_vid.stat().st_mtime and int(best_vid.stat().st_mtime) or vid_ts))
                ts = str(min(img_ts, vid_ts))  # 较早的时间
                salt = f"consolidate:{event}:{device}:{ts}"
                det_id = make_detection_id(event, device, ts, salt)
                new_dir = PHOTO_VIDEOS / event / det_id
                moves.append((img_path, new_dir / "image.jpg"))
                moves.append((best_vid, new_dir / "video.mp4"))
            else:
                # image 无配对 video → 单文件 dir
                ts = str(img_ts)
                salt = f"consolidate:{event}:{device}:{ts}"
                det_id = make_detection_id(event, device, ts, salt)
                new_dir = PHOTO_VIDEOS / event / det_id
                moves.append((img_path, new_dir / "image.jpg"))
                used.add(img_path)

        # 剩余未用 video
        for vid_path, _, vid_ts in videos:
            if vid_path in used:
                continue
            ts = str(vid_ts)
            salt = f"consolidate:{event}:{device}:{ts}"
            det_id = make_detection_id(event, device, ts, salt)
            new_dir = PHOTO_VIDEOS / event / det_id
            moves.append((vid_path, new_dir / "video.mp4"))
            used.add(vid_path)

    target_dirs = {t.parent for _, t in moves}
    img_count = sum(1 for _, t in moves if t.name == "image.jpg")
    vid_count = sum(1 for _, t in moves if t.name == "video.mp4")

    print(f"\n将创建 {len(target_dirs)} 个新 detection dirs")
    print(f"将移动 {len(moves)} 个文件 (image={img_count}, video={vid_count})")

    if moves:
        print("\nSample 前 5 个:")
        for src, dst in moves[:5]:
            print(f"  {src.relative_to(DATA_ROOT)} → {dst.relative_to(DATA_ROOT)}")

    if args.dry_run:
        print("\nDRY-RUN")
        return 0

    confirm = input(f"\n确认移动 {len(moves)} 个文件? [yes/no]: ")
    if confirm.strip().lower() != "yes":
        return 1

    for src, dst in moves:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            continue
        shutil.move(str(src), str(dst))

    # 清理空的旧 dir
    cleaned = 0
    for d in sorted(PHOTO_VIDEOS.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            cleaned += 1
    print(f"\n完成. 移动 {len(moves)} 个文件, 清理 {cleaned} 个空目录.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
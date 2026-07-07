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

    # 1. 收集所有文件, 按 (event, device_name, ts) 配对
    groups: dict[tuple, dict[str, Path]] = defaultdict(dict)
    skipped_already = 0
    skipped_unparseable: list[Path] = []

    for src_file in PHOTO_VIDEOS.rglob("*"):
        if not src_file.is_file() or src_file.name == ".gitkeep":
            continue
        parent = src_file.parent
        # 跳过已经在正确结构的 (image.jpg + video.mp4 + .gitkeep)
        if (parent / "image.jpg").exists() and (parent / "video.mp4").exists():
            skipped_already += 1
            continue

        # 解析 parent dir
        parsed = parse_parent_dir(parent.name)
        if parsed is None:
            # 也许 form 2 文件还在原路径 (pedestrian/53/20260626/)
            # parent.name 不匹配新格式, 不归本脚本管
            skipped_unparseable.append(src_file)
            continue

        event, device, ts, uuid8 = parsed
        kind = "image" if src_file.suffix.lower() == ".jpg" else "video"
        pairing_key = (event, device, ts)
        if kind in groups[pairing_key]:
            print(f"  WARN: 冲突 {pairing_key}: {groups[pairing_key][kind].relative_to(DATA_ROOT)} vs {src_file.relative_to(DATA_ROOT)}")
        groups[pairing_key][kind] = src_file

    if skipped_already:
        print(f"跳过已正确 ({skipped_already} 个)")

    if skipped_unparseable:
        print(f"未解析的 {len(skipped_unparseable)} 个文件 (form 2 原路径保留, 不动):")
        for f in skipped_unparseable[:5]:
            print(f"  {f.relative_to(DATA_ROOT)}")
        if len(skipped_unparseable) > 5:
            print(f"  ... (还有 {len(skipped_unparseable) - 5} 个)")

    # 2. 每个 pairing_key → 新 det_id dir
    moves: list[tuple[Path, Path]] = []
    for (event, device, ts), files in groups.items():
        salt = f"consolidate:{event}:{ts}"  # 同 (event, device, ts) 同 salt → 同 det_id
        det_id = make_detection_id(event, device, ts, salt)
        new_dir = PHOTO_VIDEOS / event / det_id

        for kind, src in files.items():
            ext = "jpg" if kind == "image" else "mp4"
            target = new_dir / f"{kind}.{ext}"
            if src != target:
                moves.append((src, target))

    target_dirs = {t.parent for _, t in moves}
    img_count = sum(1 for _, t in moves if t.name == "image.jpg")
    vid_count = sum(1 for _, t in moves if t.name == "video.mp4")
    pair_count = sum(1 for d in target_dirs if (d / "image.jpg").exists() and (d / "video.mp4").exists())

    print(f"\n将创建 {len(target_dirs)} 个新 detection dirs")
    print(f"将移动 {len(moves)} 个文件 (image={img_count}, video={vid_count})")
    print(f"预期成对 ({pair_count} 个双文件 dir)")

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
    for d in sorted(PHOTO_VIDEOS.rglob("*"), reverse=True()):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()
            cleaned += 1
    print(f"\n完成. 移动 {len(moves)} 个文件, 清理 {cleaned} 个空目录.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
"""Migrate all media files from old paths to new data/ tree.

Per `.omc/specs/deep-interview-photo-videos-archive.md` and
`.omc/plans/photo-videos-archive.md` (Iteration 4).

Path forms (NB-2 fix: 3 distinct shapes for snapshots/clips):
- Form 1: docs/images/2026/06/abc.jpg → data/archive/docs_images/...
- Form 2a: docs/{snapshots,clips}/{N}_{event_legacy}/{date}/x.{jpg,mp4} → active
- Form 2b: docs/{snapshots,clips}/{N}/{date}/x.{jpg,mp4} → active (event from filename)
- Form 2c: docs/{snapshots,clips}/camera_*/{date}/x.{jpg,mp4} → active (event from filename)
- Form 3: docs/monitoring/*.mp4 → data/monitoring/
                   docs/monitoring/*.avi → data/archive/monitoring_avi/ (legacy test)
- Form 4: ai-console/public/monitoring/*.mp4 → data/monitoring/
                   ai-console/public/monitoring/*.avi → data/archive/monitoring_avi/
- Form 5: output/{N}_{event_legacy}_output.mp4 → active (form 5b ffmpeg extract image.jpg)
- Form 6: output/test_999*.mp4 → delete
- Form 7: output/{N}_output.mp4 → data/archive/output/

Usage:
    python scripts/migrate_storage_paths.py --dry-run
    python scripts/migrate_storage_paths.py              # actual migration
    python scripts/migrate_storage_paths.py --rollback   # restore from log
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

# Hard precondition (Step 0 + BS-3)
assert shutil.which("ffmpeg") is not None, (
    "ffmpeg not found in PATH. Install ffmpeg >= 4.0 first."
)

PROJECT_ROOT = Path("/home/daxiong/code/console")
DATA_ROOT = PROJECT_ROOT / "data"
DOCS_ROOT = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "output"
PUB_MONITORING = PROJECT_ROOT / "ai-console" / "public" / "monitoring"

# Legacy algorithm → new short event name (per spec)
EVENT_NAME_MAP = {
    "traffic_jam": "jam",
    "vehicle_counting": "flow",
    "reverse_detection": "reverse",
    "pedestrian_intrusion": "pedestrian",
    "accident_detection": "accident",
    "vest_detection": "vest",
}
LEGACY_EVENTS = "|".join(EVENT_NAME_MAP.keys())

# Event tokens that can appear in filenames (form 2b/2c)
FILENAME_EVENT_TOKENS = (
    "pedestrian|accident|vest|jam|anomaly|flow|reverse"
)

# form 2a: {camera}_{event_legacy}/  directory segment
RE_FORM_2A_DIR = re.compile(rf"^(\d+)_(?:{LEGACY_EVENTS})$")
# form 2b: bare {N}/  directory segment
RE_FORM_2B_DIR = re.compile(r"^(\d+)$")
# form 2c: camera_* or camera_proxy_*  directory segment
RE_FORM_2C_DIR = re.compile(r"^(camera_proxy_\d+|camera_.+)$")
# filename-based event extraction (forms 2b/2c) — file is named like
#   pedestrian_147_1782910592.jpg
#   vest_262_1782120723.jpg
RE_FILENAME_EVENT = re.compile(
    rf"^({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$"
)

# output/ sub-classification (BS-2 fix)
RE_OUTPUT_ACTIVE = re.compile(rf"^(\d+)_({LEGACY_EVENTS})_output\.mp4$")
RE_OUTPUT_DELETE = re.compile(r"^test_999\d+_output\.mp4$")

LOG_FILE = PROJECT_ROOT / ".omc" / "backups" / ".migration_log.jsonl"


@dataclass
class Migration:
    src: Path
    dst: Path
    form: str
    extra: dict = field(default_factory=dict)


def classify_path(path: Path) -> Migration | None:
    """Classify a path under docs/ or ai-console/public/monitoring/."""
    try:
        rel = path.relative_to(DOCS_ROOT)
    except ValueError:
        rel = None

    if rel is not None:
        parts = rel.parts  # e.g. ('snapshots', '53_pedestrian_intrusion', '20260626', 'pedestrian_147_1782439646.jpg')
        if len(parts) < 2:
            return None

        subdir, *rest = parts
        if subdir in ("snapshots", "clips") and len(rest) >= 3:
            cam_dir, date_dir, filename = rest[0], rest[1], "/".join(rest[2:])
            # form 2a: {N}_{event} directory
            m = RE_FORM_2A_DIR.match(cam_dir)
            if m:
                cam = m.group(1)
                legacy_event = cam_dir[len(cam) + 1:]  # strip "{cam}_"
                new_event = EVENT_NAME_MAP.get(legacy_event, legacy_event)
                # keep filename as-is to preserve uniqueness
                dst = DATA_ROOT / "photo-videos" / new_event / cam / date_dir / filename
                return Migration(src=path, dst=dst, form="2a",
                                  extra={"camera": cam, "event": new_event})
            # form 2b: bare {N}
            m = RE_FORM_2B_DIR.match(cam_dir)
            if m:
                cam = m.group(1)
                # Extract event from filename
                mf = RE_FILENAME_EVENT.match(Path(filename).name)
                if mf:
                    event = mf.group(1)
                    dst = DATA_ROOT / "photo-videos" / event / cam / date_dir / filename
                    return Migration(src=path, dst=dst, form="2b",
                                      extra={"camera": cam, "event": event})
            # form 2c: camera_*
            m = RE_FORM_2C_DIR.match(cam_dir)
            if m:
                mf = RE_FILENAME_EVENT.match(Path(filename).name)
                if mf:
                    event = mf.group(1)
                    dst = DATA_ROOT / "photo-videos" / event / cam_dir / date_dir / filename
                    return Migration(src=path, dst=dst, form="2c",
                                      extra={"camera": cam_dir, "event": event})

        if subdir == "monitoring":
            # form 3: docs/monitoring/*.mp4 → active monitoring/ (production camera source)
            #         docs/monitoring/*.avi → archive/monitoring_avi/ (legacy test footage)
            if path.suffix.lower() == ".avi":
                dst = DATA_ROOT / "archive" / "monitoring_avi" / path.name
            else:
                dst = DATA_ROOT / "monitoring" / path.name
            return Migration(src=path, dst=dst, form="3")

        # form 1: docs/{images,videos,review,visualized}/... → archive
        if subdir in ("images", "videos", "review", "visualized"):
            dst = DATA_ROOT / "archive" / f"docs_{subdir}" / Path(*rest)
            return Migration(src=path, dst=dst, form="1")

    # form 4: ai-console/public/monitoring/*.{mp4,avi}
    try:
        rel_pm = path.relative_to(PUB_MONITORING)
    except ValueError:
        return None
    if rel_pm.parts:
        if path.suffix.lower() == ".avi":
            dst = DATA_ROOT / "archive" / "monitoring_avi" / path.name
        else:
            dst = DATA_ROOT / "monitoring" / path.name
        return Migration(src=path, dst=dst, form="4")

    return None


def classify_output(path: Path) -> tuple[str, Path | None, dict]:
    """Classify a file under output/."""
    name = path.name
    m = RE_OUTPUT_ACTIVE.match(name)
    if m:
        n, legacy_event = m.group(1), m.group(2)
        new_event = EVENT_NAME_MAP.get(legacy_event, legacy_event)
        dst = DATA_ROOT / "photo-videos" / new_event / n / "video.mp4"
        return ("active", dst, {"camera": n, "event": new_event, "extract_image": True})
    if RE_OUTPUT_DELETE.match(name):
        return ("delete", None, {})
    return ("archive",
            DATA_ROOT / "archive" / "output" / name,
            {})


def iter_migrations() -> list[Migration]:
    """Yield all planned migrations across docs/, output/, public/monitoring/."""
    moves: list[Migration] = []

    # docs/ subtree
    if DOCS_ROOT.exists():
        for p in DOCS_ROOT.rglob("*"):
            if p.is_file():
                mig = classify_path(p)
                if mig:
                    moves.append(mig)

    # ai-console/public/monitoring/
    if PUB_MONITORING.exists():
        for p in PUB_MONITORING.iterdir():
            if p.is_file():
                mig = classify_path(p)
                if mig:
                    moves.append(mig)

    return moves


def iter_output_actions() -> list[tuple[Path, str, Path | None, dict]]:
    """Yield output/ file actions."""
    actions = []
    if OUTPUT_DIR.exists():
        for p in OUTPUT_DIR.iterdir():
            if p.is_file():
                cls, dst, info = classify_output(p)
                actions.append((p, cls, dst, info))
    return actions


def extract_image_from_video(video_path: Path, dst_dir: Path) -> Path:
    """Run ffmpeg to extract first frame as image.jpg."""
    dst_dir.mkdir(parents=True, exist_ok=True)
    img = dst_dir / "image.jpg"
    cmd = [
        "ffmpeg", "-y", "-i", str(video_path),
        "-frames:v", "1", "-q:v", "2",
        str(img),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=60)
    return img


def perform_migration(dry_run: bool, rollback: bool) -> int:
    if rollback:
        return do_rollback()

    moves = iter_migrations()
    output_actions = iter_output_actions()

    # Print plan summary
    form_counts = Counter(m.form for m in moves)
    out_counts = Counter(a[1] for a in output_actions)

    print("=" * 60)
    print(f"Docs/migrations: {len(moves)} files")
    for form, count in sorted(form_counts.items()):
        print(f"  Form {form}: {count}")
    print(f"Output/ actions: {len(output_actions)} files")
    for cls, count in sorted(out_counts.items()):
        print(f"  {cls}: {count}")
    print(f"  EXTRACTED={out_counts['active']} (active with ffmpeg image extract)")
    print("=" * 60)

    if dry_run:
        print("DRY-RUN: no changes made.")
        return 0

    # Confirm interactive
    confirm = input("Proceed with actual migration? [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return 1

    log_entries: list[dict] = []

    # 1. docs/ subtree moves
    for mig in moves:
        mig.dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(mig.src), str(mig.dst))
        log_entries.append({
            "form": mig.form,
            "src": str(mig.src),
            "dst": str(mig.dst),
        })

    # 2. output/ actions
    for src, cls, dst, info in output_actions:
        if cls == "delete":
            src.unlink()
            log_entries.append({"form": "6", "src": str(src), "dst": None})
        elif cls == "archive":
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            log_entries.append({"form": "7", "src": str(src), "dst": str(dst)})
        elif cls == "active":
            # form 5: move video.mp4 + form 5b: extract image.jpg
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
            log_entries.append({"form": "5", "src": str(src), "dst": str(dst)})
            if info.get("extract_image"):
                try:
                    img = extract_image_from_video(dst, dst.parent)
                    log_entries.append({"form": "5b", "src": str(dst), "dst": str(img)})
                except subprocess.CalledProcessError as e:
                    print(f"WARN: ffmpeg failed for {dst}: {e}", file=sys.stderr)

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("w") as f:
        for entry in log_entries:
            f.write(json.dumps(entry) + "\n")

    print(f"Migration complete. {len(log_entries)} actions logged to {LOG_FILE}")
    return 0


def do_rollback() -> int:
    if not LOG_FILE.exists():
        print("No migration log found; nothing to rollback.")
        return 1
    count = 0
    with LOG_FILE.open() as f:
        for line in f:
            entry = json.loads(line)
            if entry.get("dst") is None:
                # delete action — cannot rollback (file is gone)
                continue
            src = Path(entry["src"])
            dst = Path(entry["dst"])
            if dst.exists():
                src.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), str(src))
                count += 1
    print(f"Rolled back {count} moves.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    return perform_migration(args.dry_run, args.rollback)


if __name__ == "__main__":
    raise SystemExit(main())
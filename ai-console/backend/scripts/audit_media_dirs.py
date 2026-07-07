#!/usr/bin/env python3
"""Audit media directories and classify them per spec rule.

Classification rule (per .omc/specs/deep-interview-photo-videos-archive.md):
- Active if code_refs(path) ∪ db_refs(path)
- Archive otherwise
- Pure test artifacts → delete

Output: /tmp/migration_plan.md with one row per directory + sub-classification
for output/ (regex A/B/C).

Usage: python scripts/audit_media_dirs.py
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/home/daxiong/code/console")
BACKEND_ROOT = PROJECT_ROOT / "ai-console" / "backend"
SRC_ROOT = PROJECT_ROOT / "ai-console" / "src"

DOCS_DIRS = [
    "snapshots",
    "clips",
    "visualized",
    "monitoring",
    "images",
    "videos",
    "review",
]

# Legacy algorithm → new short event name (per spec)
EVENT_NAME_MAP = {
    "traffic_jam": "jam",
    "vehicle_counting": "flow",
    "reverse_detection": "reverse",
    "pedestrian_intrusion": "pedestrian",
    "accident_detection": "accident",
    "vest_detection": "vest",
}

# output/ sub-classification regex (per plan §2 A3 BS-2 fix)
OUTPUT_ACTIVE_RE = re.compile(
    r"^[0-9]+_(" + "|".join(EVENT_NAME_MAP.keys()) + r")_output\.mp4$"
)
OUTPUT_DELETE_RE = re.compile(r"^test_999[0-9]+_output\.mp4$")


def code_refs_count(path: str) -> int:
    """Count grep hits for path literal in backend + frontend code."""
    pattern = path
    try:
        result = subprocess.run(
            [
                "grep", "-rn",
                "--include=*.py", "--include=*.ts", "--include=*.vue",
                "-l", pattern,
                str(BACKEND_ROOT),
                str(SRC_ROOT),
            ],
            capture_output=True, text=True, timeout=30,
        )
        # Count distinct files (one per line)
        return len([l for l in result.stdout.splitlines() if l.strip()])
    except subprocess.TimeoutExpired:
        return -1


def db_refs_count(path: str) -> int:
    """Approximate DB refs by querying the file table for storage_path prefix.

    Uses psql with the project's connection string.
    """
    sql = (
        f"SELECT count(*) FROM file "
        f"WHERE storage_path LIKE '{path}%' OR url LIKE '{path}%';"
    )
    try:
        result = subprocess.run(
            [
                "psql",
                "postgresql://postgres:e6sWVi7F8c7UneJ5sc586fTy@localhost:5434/ai_console",
                "-t", "-A", "-c", sql,
            ],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip().isdigit():
            return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError):
        pass
    return 0


def classify(code_count: int, db_count: int) -> str:
    if code_count > 0 or db_count > 0:
        return "active"
    return "archive"


def classify_output_file(filename: str) -> str:
    if OUTPUT_ACTIVE_RE.match(filename):
        return "active"
    if OUTPUT_DELETE_RE.match(filename):
        return "delete"
    return "archive"  # orphan {N}_output.mp4


def main() -> int:
    rows = []
    rows.append(
        "| Source Path | Code Refs | DB Refs | Classification |"
    )
    rows.append(
        "|-------------|-----------|---------|----------------|"
    )

    # 1. /home/daxiong/code/console/docs/{subdir}/ — 7 entries
    for sub in DOCS_DIRS:
        full = f"/home/daxiong/code/console/docs/{sub}"
        code = code_refs_count(full)
        db = db_refs_count(sub + "/")  # match storage_path LIKE 'snapshots/%'
        rows.append(
            f"| `{full}/` | {code} | {db} | {classify(code, db)} |"
        )

    # 2. /home/daxiong/code/console/output/ — classify each file
    rows.append("")
    rows.append("## output/ sub-classification")
    rows.append("")
    rows.append(
        "| File | Regex | Classification | Target Path |"
    )
    rows.append(
        "|------|-------|----------------|-------------|"
    )

    output_dir = PROJECT_ROOT / "output"
    if output_dir.exists():
        active_count = delete_count = archive_count = 0
        for f in sorted(output_dir.iterdir()):
            if not f.is_file():
                continue
            cls = classify_output_file(f.name)
            if cls == "active":
                # Match e.g. "53_accident_detection_output.mp4" → event=accident_detection, N=53
                m = OUTPUT_ACTIVE_RE.match(f.name)
                legacy = m.group(1) if m else "?"
                new_event = EVENT_NAME_MAP.get(legacy, legacy)
                n = f.name.split("_")[0]
                target = f"data/photo-videos/{new_event}/{n}/video.mp4"
                active_count += 1
            elif cls == "delete":
                target = "(deleted)"
                delete_count += 1
            else:
                n = f.name.split("_")[0]
                target = f"data/archive/output/{f.name}"
                archive_count += 1
            rows.append(f"| `{f.name}` | {'A/B/C'} | {cls} | `{target}` |")
        rows.append("")
        rows.append(
            f"**Summary**: active={active_count}, delete={delete_count}, "
            f"archive={archive_count} (total={active_count + delete_count + archive_count})"
        )

    # 3. /home/daxiong/code/console/ai-console/public/monitoring/ — monitoring fallback
    rows.append("")
    rows.append("## ai-console/public/monitoring/ (RTSP fallback)")
    rows.append("")
    pub_mon = PROJECT_ROOT / "ai-console" / "public" / "monitoring"
    if pub_mon.exists():
        files = list(pub_mon.iterdir())
        rows.append(
            f"| `ai-console/public/monitoring/` | stream.py:261 | file table | "
            f"archive | {len(files)} files |"
        )
        rows.append(
            f"→ target: `data/archive/docs_monitoring/`"
        )

    out = "\n".join(rows) + "\n"
    out_path = Path("/tmp/migration_plan.md")
    out_path.write_text(out)
    print(f"Wrote {out_path} ({len(rows)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
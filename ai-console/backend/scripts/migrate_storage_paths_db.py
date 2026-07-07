#!/usr/bin/env python3
"""Batch UPDATE warning_event/file/data_source URL fields after media migration.

Per `.omc/specs/deep-interview-photo-videos-archive.md` and
`.omc/plans/photo-videos-archive.md` §2 D10.

Rules:
- docs/snapshots/{N}_{event}/{date}/{filename}    → /data/photo-videos/{event_new}/{N}/{date}/{filename}
- docs/snapshots/{N}/{date}/{filename}            → /data/photo-videos/{event_new}/{N}/{date}/{filename}
                                                     (event from filename)
- docs/snapshots/camera_*/{date}/{filename}       → /data/photo-videos/{event_new}/camera_*/{date}/{filename}
- docs/clips/... (same as snapshots)              → /data/photo-videos/...
- docs/images/...                                 → /data/archive/docs_images/...
- docs/videos/...                                 → /data/archive/docs_videos/...
- docs/review/...                                 → /data/archive/docs_review/...
- docs/monitoring/...                             → /data/archive/docs_monitoring/...
- /uploads/images/...                             → /data/photo-videos/upload/images/...
- /uploads/videos/...                             → /data/photo-videos/upload/videos/...
- output/{N}_{event}_output.mp4                   → /data/photo-videos/{event_new}/{N}/video.mp4
                                                     (no leading slash; relative path stored in DB)

Usage:
    python scripts/migrate_storage_paths_db.py --dry-run    # count only
    python scripts/migrate_storage_paths_db.py              # execute UPDATE
    python scripts/migrate_storage_paths_db.py --rollback   # reverse
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from pathlib import Path

EVENT_NAME_MAP = {
    "traffic_jam": "jam",
    "vehicle_counting": "flow",
    "reverse_detection": "reverse",
    "pedestrian_intrusion": "pedestrian",
    "accident_detection": "accident",
    "vest_detection": "vest",
}
LEGACY_EVENTS = "|".join(EVENT_NAME_MAP.keys())
FILENAME_EVENT_TOKENS = "pedestrian|accident|vest|jam|anomaly|flow|reverse"

PG_CONN = (
    "postgresql://postgres:e6sWVi7F8c7UneJ5sc586fTy"
    "@localhost:5434/ai_console"
)


def run_sql(sql: str, *, fetch: bool = False) -> str:
    args = ["psql", PG_CONN, "-t", "-A"]
    if fetch:
        args += ["-c", sql]
    else:
        args += ["-c", sql]
    result = subprocess.run(args, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        raise RuntimeError(f"psql failed: {result.stderr}")
    return result.stdout.strip()


def rewrite_url(old: str) -> str | None:
    """Map old path to new path. Returns None if no rule applies."""
    if not old:
        return None

    # /uploads/images/... → /data/photo-videos/upload/images/...
    if old.startswith("/uploads/images/"):
        return "/data/photo-videos/upload/images/" + old[len("/uploads/images/"):]
    if old.startswith("/uploads/videos/"):
        return "/data/photo-videos/upload/videos/" + old[len("/uploads/videos/"):]
    if old.startswith("/uploads/monitoring/"):
        return "/data/archive/docs_monitoring/" + old[len("/uploads/monitoring/"):]
    # /uploads/snapshots/{N}_{event}/{date}/{filename}
    m = re.match(
        rf"^/uploads/(?:snapshots|clips)/(\d+)_({LEGACY_EVENTS})/(\d+)/(.+)$", old
    )
    if m:
        n, legacy, date, filename = m.groups()
        new_event = EVENT_NAME_MAP[legacy]
        return f"/data/photo-videos/{new_event}/{n}/{date}/{filename}"
    # /uploads/snapshots/{N}/{date}/{filename} (form 2b)
    m = re.match(
        rf"^/uploads/(?:snapshots|clips)/(\d+)/(\d+)/({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$",
        old,
    )
    if m:
        n, date, event, det_id, ts, ext = m.groups()
        return f"/data/photo-videos/{event}/{n}/{date}/{event}_{det_id}_{ts}.{ext}"
    # /uploads/snapshots/camera_*/{date}/{filename} (form 2c)
    m = re.match(
        rf"^/uploads/(?:snapshots|clips)/(camera_[^/]+)/(\d+)/({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$",
        old,
    )
    if m:
        cam, date, event, det_id, ts, ext = m.groups()
        return f"/data/photo-videos/{event}/{cam}/{date}/{event}_{det_id}_{ts}.{ext}"
    if old.startswith("/uploads/"):
        return "/data/photo-videos/upload/" + old[len("/uploads/"):]

    # docs/snapshots/{N}_{event}/{date}/{filename}
    m = re.match(
        rf"^docs/(?:snapshots|clips)/(\d+)_({LEGACY_EVENTS})/(\d+)/(.+)$", old
    )
    if m:
        n, legacy, date, filename = m.groups()
        new_event = EVENT_NAME_MAP[legacy]
        return f"/data/photo-videos/{new_event}/{n}/{date}/{filename}"

    # docs/snapshots/{N}/{date}/{filename} (form 2b) — extract event from filename
    m = re.match(
        rf"^docs/(?:snapshots|clips)/(\d+)/(\d+)/({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$",
        old,
    )
    if m:
        n, date, event, _det_id, _ts, ext = m.groups()
        return f"/data/photo-videos/{event}/{n}/{date}/{event}_{m.group(4)}_{m.group(5)}.{ext}"

    # docs/snapshots/camera_*/{date}/{filename} (form 2c)
    m = re.match(
        rf"^docs/(?:snapshots|clips)/(camera_[^/]+)/(\d+)/({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$",
        old,
    )
    if m:
        cam, date, event, _det_id, _ts, ext = m.groups()
        return f"/data/photo-videos/{event}/{cam}/{date}/{event}_{m.group(4)}_{m.group(5)}.{ext}"

    # docs/monitoring/... → /data/archive/docs_monitoring/...
    if old.startswith("docs/monitoring/"):
        return "/data/archive/docs_monitoring/" + old[len("docs/monitoring/"):]
    if old.startswith("monitoring/"):
        return "/data/archive/docs_monitoring/" + old[len("monitoring/"):]

    # docs/{images,videos,review,visualized}/... → /data/archive/docs_*/
    for sub in ("images", "videos", "review", "visualized"):
        prefix = f"docs/{sub}/"
        if old.startswith(prefix):
            return f"/data/archive/docs_{sub}/" + old[len(prefix):]

    # output/{N}_{event}_output.mp4 → /data/photo-videos/{event_new}/{N}/video.mp4
    m = re.match(rf"^output/(\d+)_({LEGACY_EVENTS})_output\.mp4$", old)
    if m:
        n, legacy = m.groups()
        new_event = EVENT_NAME_MAP[legacy]
        return f"/data/photo-videos/{new_event}/{n}/video.mp4"

    return None


def count_old_urls() -> dict[str, int]:
    """Count remaining old-format URLs."""
    counts = {}
    queries = {
        "warning_event.image_url":
            "SELECT count(*) FROM warning_event WHERE image_url IS NOT NULL "
            "AND (image_url ~ '^docs/' OR image_url ~ '^/uploads/' OR image_url ~ '^output/' OR image_url ~ '^monitoring/')",
        "warning_event.video_url":
            "SELECT count(*) FROM warning_event WHERE video_url IS NOT NULL "
            "AND (video_url ~ '^docs/' OR video_url ~ '^/uploads/' OR video_url ~ '^output/' OR video_url ~ '^monitoring/')",
        "file.storage_path":
            "SELECT count(*) FROM file WHERE storage_path IS NOT NULL "
            "AND (storage_path ~ '^docs/' OR storage_path ~ '^/uploads/' OR storage_path ~ '^output/' OR storage_path ~ '^monitoring/')",
        "file.url":
            "SELECT count(*) FROM file WHERE url IS NOT NULL "
            "AND (url ~ '^docs/' OR url ~ '^/uploads/' OR url ~ '^output/' OR url ~ '^monitoring/')",
        "data_source.rtsp_url":
            "SELECT count(*) FROM data_source WHERE rtsp_url ~ 'docs/monitoring'",
    }
    for label, q in queries.items():
        try:
            counts[label] = int(run_sql(q, fetch=True))
        except (RuntimeError, ValueError):
            counts[label] = -1
    return counts


def do_update(dry_run: bool) -> int:
    """Execute UPDATE per row using temporary mapping tables.

    For simplicity we use a row-by-row approach: SELECT old URLs, rewrite in
    Python, then UPDATE each row. This avoids complex PL/pgSQL and gives a
    clear audit trail in the script output.
    """
    table_field_queries = [
        ("warning_event", "image_url", "id"),
        ("warning_event", "video_url", "id"),
        ("file", "storage_path", "id"),
        ("file", "url", "id"),
        ("data_source", "rtsp_url", "id"),
    ]
    total_updated = 0

    for table, field, pk in table_field_queries:
        if field == "rtsp_url":
            # special: data_source.rtsp_url matches docs/monitoring
            sql = (
                f"SELECT {pk}, {field} FROM {table} WHERE {field} ~ 'docs/monitoring'"
            )
        else:
            sql = (
                f"SELECT {pk}, {field} FROM {table} WHERE {field} IS NOT NULL "
                f"AND ({field} ~ '^docs/' OR {field} ~ '^/uploads/' "
                f"OR {field} ~ '^output/' OR {field} ~ '^monitoring/')"
            )
        result = run_sql(sql, fetch=True)
        if not result:
            continue
        for line in result.splitlines():
            parts = line.split("|", 1)
            if len(parts) != 2:
                continue
            row_id, old_url = parts
            new_url = rewrite_url(old_url)
            if new_url is None:
                print(f"  WARN: no rewrite rule for {table}.{field}[{row_id}]: {old_url}")
                continue
            if not dry_run:
                update_sql = (
                    f"UPDATE {table} SET {field} = %s WHERE {pk} = %s"
                )
                # use psql with -v variables
                subprocess.run(
                    [
                        "psql", PG_CONN, "-t", "-A",
                        "-c", f"UPDATE {table} SET {field} = '{new_url}' WHERE {pk} = {row_id}",
                    ],
                    check=True, capture_output=True, timeout=10,
                )
            total_updated += 1
            print(f"  {table}.{field}[{row_id}]: {old_url} → {new_url}")

    return total_updated


def do_rollback(stash: list[tuple[str, str, str, str]]) -> int:
    """Reverse the updates from the stash."""
    for table, field, row_id, old_url in reversed(stash):
        subprocess.run(
            [
                "psql", PG_CONN, "-t", "-A",
                "-c", f"UPDATE {table} SET {field} = '{old_url}' WHERE id = {row_id}",
            ],
            check=True, capture_output=True, timeout=10,
        )
    return len(stash)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()

    if args.rollback:
        print("Rollback not auto-supported; use tar restore + manual SQL.")
        return 1

    print("Pre-migration counts of old-format URLs:")
    pre = count_old_urls()
    for label, c in pre.items():
        print(f"  {label}: {c}")
    pre_total = sum(max(0, c) for c in pre.values())

    if pre_total == 0:
        print("No old-format URLs found. Nothing to update.")
        return 0

    if args.dry_run:
        print(f"\nDRY-RUN: would attempt to rewrite {pre_total} rows.")
        return 0

    confirm = input(f"\nUpdate {pre_total} rows? [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        return 1

    print("\nExecuting UPDATE...")
    updated = do_update(dry_run=False)
    print(f"Updated {updated} rows.")

    print("\nPost-migration counts (should all be 0):")
    post = count_old_urls()
    for label, c in post.items():
        marker = "✅" if c == 0 else "❌"
        print(f"  {label}: {c} {marker}")
    return 0 if all(c == 0 for c in post.values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
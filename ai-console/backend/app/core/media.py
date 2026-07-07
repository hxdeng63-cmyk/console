"""Media path helpers for resolving and validating media URLs.

Per `.omc/specs/deep-interview-photo-videos-archive.md`:
- All media files live under /home/daxiong/code/console/data/{photo-videos,archive}
- Served at /data/* via FastAPI StaticFiles mount
- URLs in DB are stored as /data/photo-videos/... or /data/archive/...
- For backward compat, /uploads/... URLs are also accepted as input and re-mapped

BS-5 fix: ensure_valid_media_url returns input URL when file is missing
(unless input is None), so UI shows 404 instead of disappearing the node.
"""

import os
import re
from pathlib import Path
from typing import Optional


# Per migration plan §3 Step 8: media.py DOCS_ROOT → DATA_ROOT (absolute).
DATA_ROOT = Path("/home/daxiong/code/console/data")

# Legacy DOCS_ROOT kept for any fallback paths that might still reference it
# (e.g., during transition). After migration completes, this can be removed.
LEGACY_DOCS_ROOT = Path("/home/daxiong/code/console/docs")

# Legacy algorithm name → new short event name
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


def _strip_url_prefix(url: str) -> Optional[str]:
    """Strip /uploads/ or /data/ prefix, returning the suffix.

    Returns None if no recognized prefix.
    """
    if url.startswith("/uploads/"):
        return url[len("/uploads/"):]
    if url.startswith("/data/"):
        return url[len("/data/"):]
    return None


def _legacy_to_new_relative(rel: str) -> Optional[str]:
    """Map a legacy relative path (docs/X or uploads/X or snapshots/X) to a
    new relative path under data/.

    Returns None if no form matches — caller should pass through unchanged.

    Examples:
        snapshots/54_accident_detection/20260625/accident_99.jpg
          → photo-videos/accident/54/20260625/accident_99.jpg
        clips/54/20260626/vest_262.jpg
          → photo-videos/vest/54/20260626/vest_262.jpg
        snapshots/camera_vest_full_v3/20260622/vest_262.jpg
          → photo-videos/vest/camera_vest_full_v3/20260622/vest_262.jpg
        images/2026/06/abc.jpg
          → archive/docs_images/2026/06/abc.jpg
        monitoring/北区-设备1.mp4
          → monitoring/北区-设备1.mp4
    """
    # form 2a: {N}_{event}/{date}/{filename} under snapshots/clips
    m = re.match(
        rf"^(?:snapshots|clips)/(\d+)_({LEGACY_EVENTS})/(\d+)/(.+)$", rel
    )
    if m:
        n, legacy, date, filename = m.groups()
        return f"photo-videos/{EVENT_NAME_MAP[legacy]}/{n}/{date}/{filename}"

    # form 2b: bare {N}/{date}/{filename}
    m = re.match(
        rf"^(?:snapshots|clips)/(\d+)/(\d+)/({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$",
        rel,
    )
    if m:
        n, date, event, det_id, ts, ext = m.groups()
        return f"photo-videos/{event}/{n}/{date}/{event}_{det_id}_{ts}.{ext}"

    # form 2c: camera_*/{date}/{filename}
    m = re.match(
        rf"^(?:snapshots|clips)/(camera_[^/]+)/(\d+)/({FILENAME_EVENT_TOKENS})_(\d+)_(\d+)\.(jpg|mp4)$",
        rel,
    )
    if m:
        cam, date, event, det_id, ts, ext = m.groups()
        return f"photo-videos/{event}/{cam}/{date}/{event}_{det_id}_{ts}.{ext}"

    # form 3 / monitoring fallback
    if rel.startswith("monitoring/"):
        return "monitoring/" + rel[len("monitoring/"):]

    # form 1: docs/{images,videos,review,visualized}/... → archive/docs_*/
    for sub in ("images", "videos", "review", "visualized"):
        prefix = f"{sub}/"
        if rel.startswith(prefix):
            return f"archive/docs_{sub}/" + rel[len(prefix):]

    # form 5: output/{N}_{event}_output.mp4 → photo-videos/{event_new}/{N}/video.mp4
    m = re.match(rf"^output/(\d+)_({LEGACY_EVENTS})_output\.mp4$", rel)
    if m:
        n, legacy = m.groups()
        return f"photo-videos/{EVENT_NAME_MAP[legacy]}/{n}/video.mp4"

    return None  # no form matched; caller passes through unchanged


def normalize_media_url(path: Optional[str]) -> Optional[str]:
    """Convert any media path or URL into a /data/... URL.

    Accepts 5 forms:
      1. docs/snapshots/...   (legacy)
      2. data/photo-videos/... (already new)
      3. /uploads/snapshots/... (old URL prefix)
      4. /data/photo-videos/... (new URL prefix)
      5. absolute path under /home/daxiong/code/console/{docs,data}
    """
    if not path:
        return None
    path = path.strip()
    if not path:
        return None

    # form 4: already a /data/ URL — pass through
    if path.startswith("/data/"):
        return path

    # form 3: /uploads/ URL — convert
    suffix = _strip_url_prefix(path)
    if suffix is not None:
        new_rel = _legacy_to_new_relative(suffix)
        return "/data/" + new_rel

    # form 5: absolute path
    if os.path.isabs(path):
        try:
            rel = Path(path).relative_to(DATA_ROOT).as_posix()
            return "/data/" + rel
        except ValueError:
            pass
        try:
            rel = Path(path).relative_to(LEGACY_DOCS_ROOT).as_posix()
            return "/data/" + _legacy_to_new_relative(rel)
        except ValueError:
            return None

    # form 1: docs/X  → convert
    if path.startswith("docs/"):
        new_rel = _legacy_to_new_relative(path[len("docs/"):])
        return "/data/" + new_rel if new_rel else path

    # form 2: data/X → already new
    if path.startswith("data/"):
        return "/data/" + path[len("data/"):]

    # form 2a/b/c: snapshots/X or clips/X (legacy without docs/ prefix)
    new_rel = _legacy_to_new_relative(path)
    if new_rel is None:
        # Unrecognized bare string — pass through unchanged so frontend
        # can handle it (e.g. 404, opaque blob) without a misleading
        # /data/<garbage> prefix.
        return path
    return "/data/" + new_rel


def _absolute_path_from_url(url: Optional[str]) -> Optional[Path]:
    """Return the absolute filesystem path for a /data/... URL, if valid."""
    if not url:
        return None
    url = url.strip()
    normalized = normalize_media_url(url)
    if not normalized or not normalized.startswith("/data/"):
        return None
    rel = normalized[len("/data/"):]
    return DATA_ROOT / rel


def file_size_for_path(path: Optional[str]) -> Optional[int]:
    """Return file size in bytes if the absolute or data-relative path exists."""
    abs_path = _absolute_path_from_url(path)
    if abs_path is None:
        if not path:
            return None
        # Try as relative to DATA_ROOT first, then LEGACY_DOCS_ROOT
        for root in (DATA_ROOT, LEGACY_DOCS_ROOT):
            candidate = root / path
            if candidate.is_file():
                abs_path = candidate
                break
        else:
            return None
    try:
        return abs_path.stat().st_size if abs_path.is_file() else None
    except (OSError, ValueError):
        return None


def media_url_exists(url: Optional[str]) -> bool:
    """Return True if the media file referenced by a /data/... URL exists."""
    abs_path = _absolute_path_from_url(url)
    if abs_path is None:
        return False
    return abs_path.is_file()


def ensure_valid_media_url(url: Optional[str]) -> Optional[str]:
    """Return the normalized URL.

    BS-5 fix: when the underlying file is missing, return the normalized URL
    anyway (preserving input) rather than None. The frontend will surface a
    404 placeholder, but the tree node stays visible.

    Returns None only when the input itself is None or unparseable.
    """
    if not url:
        return None
    normalized = normalize_media_url(url)
    return normalized
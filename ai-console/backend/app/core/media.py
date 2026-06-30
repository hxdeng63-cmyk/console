"""Media path helpers for resolving and validating upload URLs."""

import os
from pathlib import Path
from typing import Optional


DOCS_ROOT = Path(__file__).resolve().parents[4] / "docs"


def normalize_media_url(path: Optional[str]) -> Optional[str]:
    """Convert a relative or absolute media path into a /uploads/... URL."""
    if not path:
        return None
    path = path.strip()
    if path.startswith("/uploads/"):
        return path
    if path.startswith("docs/"):
        return "/uploads/" + path[len("docs/"):]
    if os.path.isabs(path):
        try:
            rel = Path(path).relative_to(DOCS_ROOT).as_posix()
            return "/uploads/" + rel
        except ValueError:
            return None
    if path.startswith("snapshots/") or path.startswith("clips/"):
        return "/uploads/" + path
    return "/uploads/" + path


def _absolute_path_from_url(url: Optional[str]) -> Optional[Path]:
    """Return the absolute filesystem path for a /uploads/... URL, if valid."""
    if not url:
        return None
    url = url.strip()
    if url.startswith("/uploads/"):
        relative = url[len("/uploads/"):]
        return DOCS_ROOT / relative
    # Also accept raw docs/... or absolute paths for robustness
    normalized = normalize_media_url(url)
    if normalized:
        relative = normalized[len("/uploads/"):]
        return DOCS_ROOT / relative
    return None


def file_size_for_path(path: Optional[str]) -> Optional[int]:
    """Return file size in bytes if the absolute or docs-relative path exists."""
    abs_path = _absolute_path_from_url(path)
    if abs_path is None:
        if not path:
            return None
        candidate = Path(path) if os.path.isabs(path) else DOCS_ROOT / path
        abs_path = candidate
    try:
        return abs_path.stat().st_size if abs_path.is_file() else None
    except (OSError, ValueError):
        return None


def media_url_exists(url: Optional[str]) -> bool:
    """Return True if the media file referenced by a /uploads/... URL exists."""
    abs_path = _absolute_path_from_url(url)
    if abs_path is None:
        return False
    return abs_path.is_file()


def ensure_valid_media_url(url: Optional[str]) -> Optional[str]:
    """Return the normalized URL only if the underlying file exists."""
    normalized = normalize_media_url(url)
    if normalized and media_url_exists(normalized):
        return normalized
    return None

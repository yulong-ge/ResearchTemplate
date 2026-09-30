"""Safe project-relative paths used by template reads, writes, and backups."""
from __future__ import annotations

from pathlib import Path


class UnsafePathError(ValueError):
    """A managed path is invalid or escapes the project through a symlink."""


def safe_join(project_root: Path, posix_rel: str) -> Path:
    """Join a managed path without following symlink components."""
    if not isinstance(posix_rel, str) or not posix_rel or "\\" in posix_rel:
        raise UnsafePathError(f"unsafe managed path: {posix_rel!r}")
    parts = posix_rel.split("/")
    if posix_rel.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise UnsafePathError(f"unsafe managed path: {posix_rel!r}")
    if parts[0] in {".rtmpl", ".git"}:
        raise UnsafePathError(f"managed path is reserved: {posix_rel!r}")
    current = project_root.resolve()
    for part in parts:
        current /= part
        if current.is_symlink():
            raise UnsafePathError(
                f"managed path crosses a symlink: {posix_rel!r} ({current})"
            )
    return current

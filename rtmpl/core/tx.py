"""Transaction primitives: advisory lock, pending marker, atomic writes.

fcntl flock is Unix-only — rtmpl targets Mac + Linux (BatchCom). Per-file
writes use temp + ``os.replace`` (atomic rename-over); the single mutable
``state.json`` is committed last.
"""
from __future__ import annotations

import contextlib
import fcntl
import os
from pathlib import Path

LOCK_NAME = ".lock"
PENDING_NAME = ".pending"


class LockBusy(RuntimeError):
    pass


@contextlib.contextmanager
def lock(rtmpl_dir: Path):
    """Exclusive advisory lock for the project's ``.rtmpl/`` dir."""
    rtmpl_dir.mkdir(parents=True, exist_ok=True)
    lockpath = rtmpl_dir / LOCK_NAME
    fh = open(lockpath, "w")
    try:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            raise LockBusy("another rtmpl run holds the lock on this project") from e
        yield
    finally:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def mark_pending(rtmpl_dir: Path, note: str = "") -> None:
    (rtmpl_dir / PENDING_NAME).write_text(note, encoding="utf-8")


def clear_pending(rtmpl_dir: Path) -> None:
    p = rtmpl_dir / PENDING_NAME
    if p.exists():
        p.unlink()


def is_interrupted(rtmpl_dir: Path) -> bool:
    return (rtmpl_dir / PENDING_NAME).exists()


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write bytes via a temp file + fsync + atomic os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".rtmpltmp")
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, data)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, path)


def atomic_remove(path: Path) -> None:
    """Remove a file (used for safe-delete of orphans)."""
    if path.exists():
        path.unlink()

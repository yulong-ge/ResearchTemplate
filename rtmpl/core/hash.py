"""Hashing: text (CRLF→LF) vs binary (raw-byte) SHA256, POSIX path keys.

Cross-platform contract (matches the design in
docs/plans/2026-07-09-rtmpl-framework.md §3.3):
- text files (UTF-8, no NUL) hash CRLF→LF-normalized content;
- binary files (NUL / non-UTF-8) hash raw bytes, are never rendered.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path


def to_posix(path: str) -> str:
    """Normalize a path key to POSIX form (forward slashes)."""
    return path.replace(os.sep, "/").replace("\\", "/")


def is_binary(data: bytes) -> bool:
    """Detect binary content: NUL byte present, or not UTF-8 decodable."""
    if b"\x00" in data:
        return True
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return True
    return False


def hash_text(content: str) -> str:
    """SHA256 hex of CRLF→LF-normalized text."""
    return hashlib.sha256(content.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def hash_bytes(data: bytes) -> str:
    """Raw-byte SHA256 hex (binary files; no normalization)."""
    return hashlib.sha256(data).hexdigest()


def hash_data(data: bytes) -> str:
    """Hash in-memory bytes by the same text/binary rule as files."""
    if is_binary(data):
        return hash_bytes(data)
    return hash_text(data.decode("utf-8"))


def hash_file(path: Path) -> tuple[str, bool]:
    """Hash a file on disk. Returns (hex_digest, is_binary)."""
    data = path.read_bytes()
    if is_binary(data):
        return hash_bytes(data), True
    return hash_text(data.decode("utf-8")), False


def file_matches_hash(path: Path, recorded: str | None) -> bool:
    """Whether a file's current content hashes to ``recorded`` (non-null)."""
    if recorded is None:
        return False
    data = path.read_bytes()
    if is_binary(data):
        return hash_bytes(data) == recorded
    return hash_text(data.decode("utf-8")) == recorded

"""``.rtmpl/state.json``: load with health status, atomic save, path-key
validation, tombstone helpers.

Schema v2: ``{"schema": 2, "template_version": "<v>", "hashes": {<posix>: <sha256|null>}}``.
A ``null`` hash value is a tombstone (a managed file the user deleted).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

SCHEMA_VERSION = 2
STATE_FILENAME = "state.json"

# status values returned by load_state
OK = "ok"
MISSING = "missing"
CORRUPT = "corrupt"
UNSUPPORTED = "unsupported"
VERSION_UNKNOWN = "version_unknown"

_UNSAFE_PREFIXES = (".rtmpl/", ".git/")


@dataclass
class State:
    template_version: str
    hashes: dict[str, str | None] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "schema": SCHEMA_VERSION,
            "template_version": self.template_version,
            "hashes": dict(self.hashes),
        }


def is_valid_path_key(key: object) -> bool:
    """A safe managed path key: POSIX relative, no ``..``/absolute/empty
    segments, no backslash, and not under ``.rtmpl/`` or ``.git/``."""
    if not isinstance(key, str) or not key:
        return False
    if "\\" in key or key.startswith("/"):
        return False
    for seg in key.split("/"):
        if seg in ("", ".", ".."):
            return False
    if key in (".rtmpl", ".git"):
        return False
    if key.startswith(_UNSAFE_PREFIXES):
        return False
    return True


def _valid_hashes(hashes: object) -> bool:
    if not isinstance(hashes, dict):
        return False
    for k, v in hashes.items():
        if not is_valid_path_key(k):
            return False
        if v is not None and not isinstance(v, str):
            return False
    return True


def load_state(rtmpl_dir: Path) -> tuple[State | None, str]:
    """Load state.json. Returns ``(state_or_None, status)``.

    status ∈ {ok, missing, corrupt, unsupported, version_unknown}.
    Unsafe path keys → corrupt (never feed them to backup/write/delete).
    """
    path = rtmpl_dir / STATE_FILENAME
    if not path.exists():
        return None, MISSING
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None, CORRUPT
    if not isinstance(raw, dict) or raw.get("schema") != SCHEMA_VERSION:
        return None, UNSUPPORTED
    tv = raw.get("template_version")
    if not isinstance(tv, str) or not tv.strip():
        return None, VERSION_UNKNOWN
    if not _valid_hashes(raw.get("hashes")):
        return None, CORRUPT
    return State(template_version=tv, hashes=dict(raw["hashes"])), OK


def save_state(rtmpl_dir: Path, state: State) -> None:
    """Atomic save: temp file + fsync + os.replace (POSIX rename-over)."""
    rtmpl_dir.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(state.to_dict(), indent=2, ensure_ascii=False) + "\n"
    final = rtmpl_dir / STATE_FILENAME
    tmp = rtmpl_dir / f"{STATE_FILENAME}.tmp"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o644)
    try:
        os.write(fd, payload.encode("utf-8"))
        os.fsync(fd)
    finally:
        os.close(fd)
    os.replace(tmp, final)


def is_tombstone(recorded: str | None) -> bool:
    """A null recorded hash marks a user-deleted managed file."""
    return recorded is None

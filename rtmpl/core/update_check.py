"""Outdated-installment banner.

Agents (and humans) often reuse a stale `uv tool install` of rtmpl. This module
compares the running version against the canonical `pyproject.toml` on the
default branch of the source repository and, when the running copy is older,
prints an actionable banner on stderr telling the agent to upgrade BEFORE using
the tool. The check never blocks: network failure, CI, or
``RTMPL_NO_UPDATE_CHECK=1`` degrade to silence.
"""
from __future__ import annotations

import json
import os
import re
import tempfile
import time
import urllib.request
from pathlib import Path

REPO_RAW_VERSION_URL = (
    "https://raw.githubusercontent.com/yulong-ge/ResearchTemplate/main/pyproject.toml"
)
UPGRADE_CMD = "uv tool install --upgrade git+https://github.com/yulong-ge/ResearchTemplate"
CACHE_TTL_SECONDS = 6 * 3600
_NO_CHECK_ENV = "RTMPL_NO_UPDATE_CHECK"
_TTL_ENV = "RTMPL_UPDATE_CHECK_TTL"
_TIMEOUT_SECONDS = 5

_VERSION_RE = re.compile(r'^version\s*=\s*"([^"]+)"', re.MULTILINE)


def _cache_path() -> Path:
    override = os.environ.get("RTMPL_UPDATE_CACHE")
    if override:
        return Path(override)
    xdg = os.environ.get("XDG_CACHE_HOME") or str(Path.home() / ".cache")
    return Path(xdg) / "rtmpl" / "update-check.json"


def _cmp_tuple(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in v.split("."):
        m = re.match(r"\d+", chunk)
        parts.append(int(m.group()) if m else 0)
    return tuple(parts)


def _is_newer(latest: str, current: str) -> bool:
    return _cmp_tuple(latest) > _cmp_tuple(current)


def _fetch_remote_version() -> str | None:
    """Read the version line from the canonical pyproject.toml; None on failure."""
    req = urllib.request.Request(
        REPO_RAW_VERSION_URL, headers={"User-Agent": "rtmpl-update-check"}
    )
    try:
        with urllib.request.urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
            body = resp.read().decode("utf-8", errors="replace")
    except Exception:
        return None  # offline / proxy block / DNS failure — treat as unknown
    m = _VERSION_RE.search(body)
    return m.group(1) if m else None


def _load_cache(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _save_cache(path: Path, payload: dict) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".update-check.")
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh)
        os.replace(tmp, path)
    except Exception:
        pass  # cache is best-effort only


def latest_known_version(current: str) -> str | None:
    """Return the latest published version, or None when unknown.

    consults a TTL cache; ``None`` means "no statement" (offline, disabled, or
    unparsable remote) and MUST NOT be treated as "up to date" or "outdated".
    """
    if os.environ.get(_NO_CHECK_ENV, "") not in ("", "0", "false", "False"):
        return None
    ttl = CACHE_TTL_SECONDS
    try:
        ttl = int(os.environ.get(_TTL_ENV, CACHE_TTL_SECONDS))
    except ValueError:
        pass

    cache = _cache_path()
    now = time.time()
    data = _load_cache(cache)
    if isinstance(data, dict):
        cached_at, cached_v = data.get("checked_at", 0), data.get("version")
        if now - float(cached_at) < ttl and isinstance(cached_v, str):
            return cached_v

    try:
        remote = _fetch_remote_version()
    except Exception:
        remote = None  # offline / proxy block / DNS failure — treat as unknown
    if remote is not None:
        _save_cache(cache, {"checked_at": now, "version": remote})
    return remote


def staleness_banner(current: str, latest: str | None) -> str | None:
    """Banner text when the running install is outdated, else None."""
    if latest is None or not _is_newer(latest, current):
        return None
    return (
        f"[rtmpl] OUTDATED: running {current}, latest is {latest}. "
        "Update BEFORE using the tool:\n"
        f"  {UPGRADE_CMD}\n"
        f"(set {_NO_CHECK_ENV}=1 to silence)"
    )

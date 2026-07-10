"""Pre-mutation backup: snapshot every disk-present universe path + manifest.json.

The manifest records per-path pre-run presence + hash so a manual restore (after
an interrupted run) knows which newly-created files to delete.
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from . import hash as hashmod


def _local(project_root: Path, posix_rel: str) -> Path:
    return project_root.joinpath(*posix_rel.split("/"))


def create_backup(
    rtmpl_dir: Path,
    project_root: Path,
    universe_paths: list[str],
    extra: dict | None = None,
) -> Path:
    """Snapshot disk-present universe paths into ``.rtmpl/.backup-<ts>/`` and
    write ``manifest.json``. Returns the backup directory."""
    ts = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    bdir = rtmpl_dir / f".backup-{ts}"
    manifest: dict = {"created": ts, "paths": {}}
    if extra:
        manifest.update(extra)
    for rel in sorted(universe_paths):
        src = _local(project_root, rel)
        present = src.exists()
        entry: dict = {"present": present}
        if present:
            h, _binary = hashmod.hash_file(src)
            entry["hash"] = h
            dst = bdir.joinpath(*rel.split("/"))
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        manifest["paths"][rel] = entry
    bdir.mkdir(parents=True, exist_ok=True)
    (bdir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return bdir

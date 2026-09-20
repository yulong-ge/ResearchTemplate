"""Total 8-row classifier over the update universe.

Universe = ``current_template_paths ∪ recorded_paths``. For each path the
classifier decides one of: unchanged / autoUpdate / new / changed /
userDeleted / orphanedPristine / orphanedModified / deadOrphan — covering every
``recorded`` value (hash / null tombstone / absent). See plan §5.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import hash as hashmod
from .state import MANAGED, SEED_ONLY

UNCHANGED = "unchanged"
AUTOUPDATE = "autoUpdate"
NEW = "new"
CHANGED = "changed"
USERDELETED = "userDeleted"
ORPHANED_PRISTINE = "orphanedPristine"
ORPHANED_MODIFIED = "orphanedModified"
DEADORPHAN = "deadOrphan"
SEEDONLY = "seedOnly"

# Sentinel for "path not present in recorded hashes" (distinct from a null tombstone).
ABSENT = object()

# States that require a user decision (prompt) during update. orphanedModified
# is auto-preserved (no prompt); userDeleted is auto-tombstoned; deadOrphan
# auto-pruned.
PROMPT_STATES = {CHANGED, ORPHANED_PRISTINE}


@dataclass
class FileState:
    path: str
    state: str
    in_template: bool
    on_disk: bool
    ownership: str = MANAGED

    @property
    def needs_prompt(self) -> bool:
        return self.state in PROMPT_STATES


def _local_path(project_root: Path, posix_rel: str) -> Path:
    return project_root.joinpath(*posix_rel.split("/"))


def classify_path(
    in_tmpl: bool,
    on_disk: bool,
    disk_eq_tmpl: bool,
    recorded: object,
    disk_hash: str | None,
    ownership: str = MANAGED,
) -> str:
    """Classify one path. ``recorded`` is a hex str, ``None`` (tombstone), or ABSENT."""
    if ownership == SEED_ONLY:
        if on_disk:
            return SEEDONLY
        return NEW if recorded is ABSENT else USERDELETED
    rec_matches_disk = isinstance(recorded, str) and disk_hash is not None and recorded == disk_hash
    if in_tmpl:
        if on_disk:
            if disk_eq_tmpl:
                return UNCHANGED
            return AUTOUPDATE if rec_matches_disk else CHANGED
        return NEW if recorded is ABSENT else USERDELETED
    # not in template → only present via recorded (orphan quadrant)
    if on_disk:
        return ORPHANED_PRISTINE if rec_matches_disk else ORPHANED_MODIFIED
    return DEADORPHAN


def classify_universe(
    project_root: Path,
    current_template: dict[str, bytes],
    recorded_hashes: dict[str, str | None],
    ownership: dict[str, str] | None = None,
    policy_for=None,
) -> list[FileState]:
    """Classify every path in ``current_template ∪ recorded_hashes``."""
    ownership = ownership or {}
    universe = set(current_template) | set(recorded_hashes) | set(ownership)
    results: list[FileState] = []
    for rel in sorted(universe):
        in_tmpl = rel in current_template
        disk_path = _local_path(project_root, rel)
        on_disk = disk_path.exists()
        disk_eq_tmpl = False
        disk_hash: str | None = None
        if on_disk:
            disk_hash, _binary = hashmod.hash_file(disk_path)
            if in_tmpl:
                disk_eq_tmpl = disk_path.read_bytes() == current_template[rel]
        recorded = recorded_hashes.get(rel, ABSENT)
        owner = ownership.get(rel)
        if owner is None and in_tmpl and policy_for is not None:
            owner = policy_for(rel)
        owner = owner or MANAGED
        state = classify_path(in_tmpl, on_disk, disk_eq_tmpl, recorded, disk_hash, owner)
        results.append(FileState(rel, state, in_tmpl, on_disk, owner))
    return results

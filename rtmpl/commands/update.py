"""`rtmpl update` — sync template improvements into the current project.

Flow (plan §4): lock → health → skew → classify → report → [dry-run exit] →
resolve → backup → apply → commit state. The single mutable ``state.json`` is
committed last as one atomic replace after all file writes.
"""
from __future__ import annotations

from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core import version as versionmod
from ..core.backup import create_backup
from ..core.classify import (
    AUTOUPDATE,
    CHANGED,
    DEADORPHAN,
    NEW,
    ORPHANED_MODIFIED,
    ORPHANED_PRISTINE,
    UNCHANGED,
    USERDELETED,
    classify_universe,
)
from ..core.state import OK, State, load_state, save_state
from ..core.template import load_manifest, walk_payload
from ..core.tx import (
    LockBusy,
    atomic_remove,
    atomic_write_bytes,
    clear_pending,
    is_interrupted,
    lock,
    mark_pending,
)
from ._common import (
    CommandError,
    format_report,
    local_path,
    load_config,
    report,
    rtmpl_dir,
    save_config,
    values_from_config,
)


def _write_new(path: Path, data: bytes) -> None:
    """Write a collision-safe ``.new`` review copy (never overwrites a leftover)."""
    base = Path(str(path) + ".new")
    target = base
    if base.exists():
        i = 1
        while Path(str(path) + f".new.{i}").exists():
            i += 1
        target = Path(str(path) + f".new.{i}")
    atomic_write_bytes(target, data)
    print(f"  created {target.name}")


def _resolve(prompts, args) -> dict[str, str]:
    if not prompts:
        return {}
    decisions: dict[str, str] = {}
    if getattr(args, "force", False):
        for fs in prompts:
            decisions[fs.path] = "overwrite" if fs.state == CHANGED else "delete"
        return decisions
    if getattr(args, "skip", False):
        for fs in prompts:
            decisions[fs.path] = "skip"
        return decisions
    if getattr(args, "no_input", False):
        raise CommandError(
            "unresolved decisions under --no-input: "
            + ", ".join(p.path for p in prompts)
            + " (use --force/--skip)"
        )
    for fs in prompts:
        if fs.state == CHANGED:
            choice = (
                input(f"{fs.path} changed [1]overwrite [2]skip [3]create-new (2): ").strip()
                or "2"
            )
            decisions[fs.path] = {"1": "overwrite", "2": "skip", "3": "create-new"}.get(
                choice, "skip"
            )
        elif fs.state == ORPHANED_PRISTINE:
            choice = (
                input(f"{fs.path} orphaned & pristine [y]delete [n]keep (n): ").strip() or "n"
            )
            decisions[fs.path] = "delete" if choice == "y" else "keep"
    return decisions


def _apply(states, decisions, project_root, rendered, old_hashes) -> dict[str, str | None]:
    new_hashes: dict[str, str | None] = {}
    for fs in states:
        rel = fs.path
        rec = old_hashes.get(rel)
        st = fs.state
        if st == UNCHANGED:
            new_hashes[rel] = hashmod.hash_data(rendered[rel])  # state-heal
        elif st == AUTOUPDATE:
            atomic_write_bytes(local_path(project_root, rel), rendered[rel])
            new_hashes[rel] = hashmod.hash_data(rendered[rel])
        elif st == NEW:
            atomic_write_bytes(local_path(project_root, rel), rendered[rel])
            new_hashes[rel] = hashmod.hash_data(rendered[rel])
        elif st == CHANGED:
            d = decisions.get(rel)
            if d == "overwrite":
                atomic_write_bytes(local_path(project_root, rel), rendered[rel])
                new_hashes[rel] = hashmod.hash_data(rendered[rel])
            elif d == "create-new":
                _write_new(local_path(project_root, rel), rendered[rel])
                new_hashes[rel] = rec  # keep old
            else:  # skip
                new_hashes[rel] = rec
        elif st == USERDELETED:
            new_hashes[rel] = None  # tombstone
        elif st == ORPHANED_PRISTINE:
            if decisions.get(rel) == "delete":
                atomic_remove(local_path(project_root, rel))  # entry dropped
            else:
                new_hashes[rel] = rec  # keep
        elif st == ORPHANED_MODIFIED:
            new_hashes[rel] = rec  # preserve
        elif st == DEADORPHAN:
            pass  # prune (entry not added)
    return new_hashes


def run(args) -> int:
    project_root = Path.cwd()
    rd = rtmpl_dir(project_root)
    try:
        with lock(rd):
            return _run_locked(args, project_root, rd)
    except LockBusy as e:
        raise CommandError(str(e))


def _run_locked(args, project_root: Path, rd: Path) -> int:
    if is_interrupted(rd):
        raise CommandError(
            "previous update was interrupted (.rtmpl/.pending present); "
            "restore from the latest .rtmpl/.backup-*/ then remove .pending"
        )
    state, status = load_state(rd)
    if status != OK:
        if status == "missing":
            raise CommandError("not an rtmpl project; run `rtmpl new` or `rtmpl adopt`")
        raise CommandError(f"state.json is {status}; run `rtmpl repair`")
    cfg = load_config(project_root)
    if not cfg:
        raise CommandError("no .rtmpl/config.yaml; run `rtmpl adopt`")
    template = cfg.get("template")
    if not template:
        raise CommandError("config.yaml has no template field")
    manifest = load_manifest(template)

    skew = versionmod.compare(manifest.version, state.template_version)
    if skew == versionmod.DOWNGRADE and not getattr(args, "allow_downgrade", False):
        raise CommandError(
            f"installed template {manifest.version} is older than project "
            f"{state.template_version}; use --allow-downgrade"
        )

    values = values_from_config(manifest, cfg)
    backfill = False
    for var in manifest.variables:
        if var.field not in cfg and var.default is not None:
            cfg[var.field] = var.default
            values[var.field] = var.default
            backfill = True
    for var in manifest.variables:
        if var.field not in values and var.required and var.default is None:
            raise CommandError(
                f"template requires new variable {var.field!r} without default; "
                "run `rtmpl adopt` to collect it"
            )

    rendered = rendermod.render_payload(walk_payload(template, manifest), manifest, values)
    states = classify_universe(project_root, rendered, state.hashes)
    print(format_report(report(states)))

    if getattr(args, "dry_run", False):
        return 0

    prompts = [s for s in states if s.needs_prompt]
    decisions = _resolve(prompts, args)

    universe = sorted(set(rendered) | set(state.hashes))
    bdir = create_backup(
        rd, project_root, universe, extra={"template_version_before": state.template_version}
    )
    print(f"Backup: {bdir.relative_to(project_root)}/")

    mark_pending(rd, note=f"update {template} {manifest.version}")
    try:
        new_hashes = _apply(states, decisions, project_root, rendered, state.hashes)
        if backfill:
            save_config(project_root, cfg)
        save_state(rd, State(template_version=manifest.version, hashes=new_hashes))
    finally:
        clear_pending(rd)
    print(f"Updated to {template} @ {manifest.version}")
    return 0

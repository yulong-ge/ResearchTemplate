"""`rtmpl update` — sync template improvements into the current project.

The read-only plan is built before any mutation. ``status`` uses the same plan
builder without taking the write lock, while ``update`` applies the reviewed
plan under the project lock.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
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
    FileState,
    classify_universe,
)
from ..core.state import OK, State, load_state, save_state
from ..core.template import TemplateManifest, load_manifest, walk_payload
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


@dataclass
class UpdatePlan:
    project_root: Path
    rtmpl_path: Path
    template: str
    manifest: TemplateManifest
    config: dict
    state: State
    rendered: dict[str, bytes]
    states: list[FileState]
    backfill_config: bool


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


def build_plan(args, project_root: Path | None = None) -> UpdatePlan:
    """Build a complete read-only update plan for the current project."""
    project_root = project_root or Path.cwd()
    rd = rtmpl_dir(project_root)
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

    config = load_config(project_root)
    if config is None:
        raise CommandError("no .rtmpl/config.yaml; run `rtmpl adopt`")
    if not isinstance(config, dict):
        raise CommandError("config.yaml root must be a mapping")
    template = config.get("template")
    if not isinstance(template, str) or not template:
        raise CommandError("config.yaml has no template field")
    manifest = load_manifest(template)

    skew = versionmod.compare(manifest.version, state.template_version)
    if skew == versionmod.DOWNGRADE and not getattr(args, "allow_downgrade", False):
        raise CommandError(
            f"installed template {manifest.version} is older than project "
            f"{state.template_version}; use --allow-downgrade"
        )

    try:
        values = rendermod.validate_values(
            manifest, values_from_config(manifest, config)
        )
    except rendermod.RenderError as exc:
        raise CommandError(f"invalid config.yaml values: {exc}") from exc
    backfill_config = False
    for var in manifest.variables:
        if var.field not in config and var.default is not None:
            config[var.field] = var.default
            values[var.field] = var.default
            backfill_config = True
    for var in manifest.variables:
        if var.field not in values and var.required and var.default is None:
            raise CommandError(
                f"template requires new variable {var.field!r} without default; "
                "run `rtmpl adopt` to collect it"
            )

    rendered = rendermod.render_payload(walk_payload(template, manifest), manifest, values)
    try:
        rendermod.check_render_residuals(rendered, manifest)
    except rendermod.RenderError as exc:
        raise CommandError(f"template rendering failed: {exc}") from exc
    states = classify_universe(project_root, rendered, state.hashes)
    return UpdatePlan(
        project_root=project_root,
        rtmpl_path=rd,
        template=template,
        manifest=manifest,
        config=config,
        state=state,
        rendered=rendered,
        states=states,
        backfill_config=backfill_config,
    )


def plan_as_dict(plan: UpdatePlan) -> dict:
    def action(file_state: FileState) -> str:
        return {
            NEW: "add",
            AUTOUPDATE: "overwrite",
            UNCHANGED: "skip",
            CHANGED: "decide",
            USERDELETED: "preserve-deletion",
            ORPHANED_PRISTINE: "decide-delete-or-keep",
            ORPHANED_MODIFIED: "preserve",
            DEADORPHAN: "prune-state",
        }[file_state.state]

    def reason(file_state: FileState) -> str | None:
        return {
            CHANGED: "disk content differs from the recorded template baseline",
            ORPHANED_PRISTINE: "path is no longer in the template and matches its recorded baseline",
            ORPHANED_MODIFIED: "path is no longer in the template and has local changes",
            USERDELETED: "path was previously managed but is absent on disk",
            DEADORPHAN: "path is absent from both the template and disk",
        }.get(file_state.state)

    groups = report(plan.states)
    return {
        "template": plan.template,
        "schema": plan.manifest.schema,
        "template_version": plan.manifest.version,
        "project_root": str(plan.project_root),
        "backfill_config": plan.backfill_config,
        "summary": {state: len(items) for state, items in sorted(groups.items())},
        "files": [
            {
                "path": file_state.path,
                "state": file_state.state,
                "in_template": file_state.in_template,
                "on_disk": file_state.on_disk,
                "needs_decision": file_state.needs_prompt,
                "suggested_action": action(file_state),
                "conflict_reason": reason(file_state),
            }
            for file_state in plan.states
        ],
    }


def print_plan(plan: UpdatePlan, *, as_json: bool = False) -> None:
    if as_json:
        print(json.dumps(plan_as_dict(plan), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(format_report(report(plan.states)))


def _paths(args, name: str) -> set[str]:
    return set(getattr(args, name, []) or [])


def _resolve(prompts: list[FileState], args) -> dict[str, str]:
    prompt_paths = {file_state.path for file_state in prompts}
    accept = _paths(args, "accept")
    skip = _paths(args, "skip")
    create_new = _paths(args, "create_new")
    requested = {"accept": accept, "skip": skip, "create-new": create_new}
    for option, paths in requested.items():
        unknown = sorted(paths - prompt_paths)
        if unknown:
            raise CommandError(
                f"--{option} path is not awaiting a decision: {', '.join(unknown)}"
            )
    overlaps = [
        (left, right)
        for left, right in (("accept", "skip"), ("accept", "create-new"), ("skip", "create-new"))
        if requested[left] & requested[right]
    ]
    if overlaps:
        left, right = overlaps[0]
        paths = ", ".join(sorted(requested[left] & requested[right]))
        raise CommandError(f"a path cannot use both --{left} and --{right}: {paths}")
    if not prompts:
        return {}

    decisions: dict[str, str] = {}
    for file_state in prompts:
        path = file_state.path
        if path in accept:
            decisions[path] = "overwrite" if file_state.state == CHANGED else "delete"
        elif path in skip:
            decisions[path] = "skip" if file_state.state == CHANGED else "keep"
        elif path in create_new:
            if file_state.state != CHANGED:
                raise CommandError(f"--create-new only applies to changed files: {path}")
            decisions[path] = "create-new"
        elif getattr(args, "no_input", False):
            raise CommandError(
                "unresolved decisions under --no-input: "
                + ", ".join(item.path for item in prompts if item.path not in decisions)
                + " (use --accept PATH, --skip PATH, or --create-new PATH)"
            )
        elif file_state.state == CHANGED:
            choice = (
                input(f"{path} changed [1]overwrite [2]skip [3]create-new (2): ").strip()
                or "2"
            )
            decisions[path] = {"1": "overwrite", "2": "skip", "3": "create-new"}.get(
                choice, "skip"
            )
        elif file_state.state == ORPHANED_PRISTINE:
            choice = input(f"{path} orphaned & pristine [y]delete [n]keep (n): ").strip() or "n"
            decisions[path] = "delete" if choice == "y" else "keep"
    return decisions


def _apply(states, decisions, project_root, rendered, old_hashes) -> dict[str, str | None]:
    new_hashes: dict[str, str | None] = {}
    for fs in states:
        rel = fs.path
        rec = old_hashes.get(rel)
        st = fs.state
        if st == UNCHANGED:
            new_hashes[rel] = hashmod.hash_data(rendered[rel])
        elif st == AUTOUPDATE:
            atomic_write_bytes(local_path(project_root, rel), rendered[rel])
            new_hashes[rel] = hashmod.hash_data(rendered[rel])
        elif st == NEW:
            atomic_write_bytes(local_path(project_root, rel), rendered[rel])
            new_hashes[rel] = hashmod.hash_data(rendered[rel])
        elif st == CHANGED:
            decision = decisions.get(rel)
            if decision == "overwrite":
                atomic_write_bytes(local_path(project_root, rel), rendered[rel])
                new_hashes[rel] = hashmod.hash_data(rendered[rel])
            elif decision == "create-new":
                _write_new(local_path(project_root, rel), rendered[rel])
                new_hashes[rel] = rec
            else:
                new_hashes[rel] = rec
        elif st == USERDELETED:
            new_hashes[rel] = None
        elif st == ORPHANED_PRISTINE:
            if decisions.get(rel) == "delete":
                atomic_remove(local_path(project_root, rel))
            else:
                new_hashes[rel] = rec
        elif st == ORPHANED_MODIFIED:
            new_hashes[rel] = rec
        elif st == DEADORPHAN:
            pass
    return new_hashes


def run(args) -> int:
    if getattr(args, "json", False) and not getattr(args, "dry_run", False):
        raise CommandError("--json is only supported with --dry-run")
    project_root = Path.cwd()
    rd = rtmpl_dir(project_root)
    if getattr(args, "dry_run", False):
        return _run_locked(args, project_root)
    try:
        with lock(rd):
            return _run_locked(args, project_root)
    except LockBusy as e:
        raise CommandError(str(e))


def _run_locked(args, project_root: Path) -> int:
    plan = build_plan(args, project_root)
    if getattr(args, "dry_run", False):
        print_plan(plan, as_json=getattr(args, "json", False))
        return 0

    print_plan(plan)
    prompts = [file_state for file_state in plan.states if file_state.needs_prompt]
    decisions = _resolve(prompts, args)

    universe = sorted(set(plan.rendered) | set(plan.state.hashes))
    backup_dir = create_backup(
        plan.rtmpl_path,
        project_root,
        universe,
        extra={"template_version_before": plan.state.template_version},
    )
    print(f"Backup: {backup_dir.relative_to(project_root)}/")

    mark_pending(plan.rtmpl_path, note=f"update {plan.template} {plan.manifest.version}")
    committed = False
    try:
        new_hashes = _apply(
            plan.states,
            decisions,
            project_root,
            plan.rendered,
            plan.state.hashes,
        )
        if plan.backfill_config:
            save_config(project_root, plan.config)
        save_state(
            plan.rtmpl_path,
            State(template_version=plan.manifest.version, hashes=new_hashes),
        )
        committed = True
    finally:
        if committed:
            clear_pending(plan.rtmpl_path)
    print(f"Updated to {plan.template} @ {plan.manifest.version}")
    return 0

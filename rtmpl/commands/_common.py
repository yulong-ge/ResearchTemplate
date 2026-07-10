"""Shared helpers for commands: project/config location, variable collection,
and the change report.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml

from ..core import render as rendermod
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
)
from ..core.template import TemplateManifest, list_templates
from ..core.tx import atomic_write_bytes

RTMPL_DIRNAME = ".rtmpl"
CONFIG_NAME = "config.yaml"


class CommandError(Exception):
    """A user-facing command error (message is printed by the CLI)."""

# Symbol/label per state for the report.
_STATE_LABEL = {
    NEW: ("+", "New files (will add)"),
    AUTOUPDATE: ("↑", "Template updated (will auto-update)"),
    UNCHANGED: ("○", "Unchanged (will skip)"),
    CHANGED: ("?", "Modified by you (need your decision)"),
    USERDELETED: ("✕", "Deleted by you (preserved)"),
    ORPHANED_PRISTINE: ("⊘", "Orphaned, pristine (safe-delete candidate)"),
    ORPHANED_MODIFIED: ("⊘!", "Orphaned, modified (preserved)"),
    DEADORPHAN: ("∅", "Dead orphan (will prune from state)"),
}


def rtmpl_dir(project_root: Path) -> Path:
    return project_root / RTMPL_DIRNAME


def default_template() -> str:
    """Pick the sole available template, or error if ambiguous/none."""
    names = list_templates()
    if len(names) == 1:
        return names[0]
    if not names:
        raise CommandError("no templates installed")
    raise CommandError(f"multiple templates; specify --template (available: {', '.join(names)})")


def load_config(project_root: Path) -> dict | None:
    p = rtmpl_dir(project_root) / CONFIG_NAME
    if not p.exists():
        return None
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def save_config(project_root: Path, config: dict) -> None:
    rd = rtmpl_dir(project_root)
    rd.mkdir(parents=True, exist_ok=True)
    payload = yaml.safe_dump(config, sort_keys=False, allow_unicode=True).encode("utf-8")
    atomic_write_bytes(rd / CONFIG_NAME, payload)


def collect_variables(
    manifest: TemplateManifest, flag_values: dict[str, str], no_input: bool
) -> dict[str, str]:
    """Collect variable values from flags, then prompts (unless --no-input),
    then validate + default-fill. Raises on missing required / invalid."""
    values: dict[str, str] = {}
    for var in manifest.variables:
        if var.field in flag_values:
            values[var.field] = flag_values[var.field]
        elif not no_input:
            values[var.field] = input(f"{var.prompt or var.field}: ").strip()
    return rendermod.validate_values(manifest, values)


def values_from_config(manifest: TemplateManifest, config: dict) -> dict[str, str]:
    """Pull variable values out of config.yaml (by field name)."""
    return {v.field: config[v.field] for v in manifest.variables if v.field in config}


def config_for_new(template_name: str, values: dict[str, str]) -> dict:
    cfg = {"template": template_name, "created_at": date.today().isoformat()}
    for k, v in values.items():
        cfg[k] = v
    return cfg


def local_path(project_root: Path, posix_rel: str) -> Path:
    return project_root.joinpath(*posix_rel.split("/"))


def report(states: list[FileState]) -> dict[str, list[FileState]]:
    """Group FileStates by category. Returns groups; callers print."""
    groups: dict[str, list[FileState]] = {}
    for fs in states:
        groups.setdefault(fs.state, []).append(fs)
    return groups


def format_report(groups: dict[str, list[FileState]]) -> str:
    lines: list[str] = []
    order = [
        NEW,
        AUTOUPDATE,
        CHANGED,
        ORPHANED_PRISTINE,
        ORPHANED_MODIFIED,
        USERDELETED,
        DEADORPHAN,
        UNCHANGED,
    ]
    for st in order:
        items = groups.get(st, [])
        if not items:
            continue
        sym, label = _STATE_LABEL[st]
        lines.append(f"{label}:")
        show = items if st != UNCHANGED else items[:5]
        for fs in show:
            lines.append(f"  {sym} {fs.path}")
        if st == UNCHANGED and len(items) > 5:
            lines.append(f"    ... and {len(items) - 5} more")
        lines.append("")
    return "\n".join(lines)

"""`rtmpl adopt` — bring an existing ``cp`` project under rtmpl management.

Records the rendered current-template hash for disk-present files (so customized
files classify as ``changed`` on the first update, never auto-clobbered) and
Omits missing managed files (so they become ``new`` on the first update) while
keeping missing seed-only records as tombstones. Never edits business files.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core.state import MANAGED, OK, SEED_ONLY, State, load_state, save_state
from ..core.template import load_manifest, walk_payload
from ._common import (
    collect_variables,
    default_template,
    local_path,
    load_config,
    ownership_for,
    rtmpl_dir,
    save_config,
    values_from_config,
)


def run(args) -> int:
    project_root = Path.cwd()
    template = args.template or default_template()
    manifest = load_manifest(template)
    existing = load_config(project_root)
    previous_state, previous_status = load_state(rtmpl_dir(project_root))
    previous_ownership = (
        dict(previous_state.ownership)
        if previous_state is not None and previous_status == OK
        else {}
    )

    flag_values: dict[str, str] = dict(getattr(args, "var", {}) or {})
    if existing and not getattr(args, "repair", False) and not flag_values:
        values = rendermod.validate_values(manifest, values_from_config(manifest, existing))
    else:
        values = collect_variables(manifest, flag_values, args.no_input)

    rendered = rendermod.render_payload(walk_payload(template, manifest), manifest, values)

    # adopt semantics: baseline = template hash for disk-present files; omit missing
    hashes: dict[str, str | None] = {}
    ownership: dict[str, str] = dict(previous_ownership)
    for rel, data in rendered.items():
        owner = ownership_for(previous_ownership, rel, manifest)
        ownership[rel] = SEED_ONLY if owner == SEED_ONLY else MANAGED
        path = local_path(project_root, rel)
        if path.exists():
            hashes[rel] = hashmod.hash_file(path)[0] if owner == SEED_ONLY else hashmod.hash_data(data)
        elif owner == SEED_ONLY:
            hashes[rel] = None

    cfg = dict(existing) if existing else {}
    cfg["template"] = template
    cfg.setdefault("created_at", date.today().isoformat())
    for k, v in values.items():
        cfg[k] = v
    save_config(project_root, cfg)
    save_state(
        rtmpl_dir(project_root),
        State(template_version=manifest.version, hashes=hashes, ownership=ownership),
    )

    print(
        f"Adopted {project_root} (template {template} @ {manifest.version}); "
        f"{len(hashes)} files baselined"
    )
    return 0

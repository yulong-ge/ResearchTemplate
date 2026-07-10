"""`rtmpl adopt` — bring an existing ``cp`` project under rtmpl management.

Records the rendered current-template hash for disk-present files (so customized
files classify as ``changed`` on the first update, never auto-clobbered) and
OMITS missing current-template files (so they become ``new`` on the first
update). Never edits business files.
"""
from __future__ import annotations

from datetime import date
from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core.state import State, save_state
from ..core.template import load_manifest, walk_payload
from ._common import (
    collect_variables,
    default_template,
    local_path,
    load_config,
    rtmpl_dir,
    save_config,
    values_from_config,
)


def run(args) -> int:
    project_root = Path.cwd()
    template = args.template or default_template()
    manifest = load_manifest(template)
    existing = load_config(project_root)

    flag_values: dict[str, str] = dict(getattr(args, "var", {}) or {})
    if existing and not getattr(args, "repair", False) and not flag_values:
        values = rendermod.validate_values(manifest, values_from_config(manifest, existing))
    else:
        values = collect_variables(manifest, flag_values, args.no_input)

    rendered = rendermod.render_payload(walk_payload(template, manifest), manifest, values)

    # adopt semantics: baseline = template hash for disk-present files; omit missing
    hashes: dict[str, str | None] = {}
    for rel, data in rendered.items():
        if local_path(project_root, rel).exists():
            hashes[rel] = hashmod.hash_data(data)

    cfg = dict(existing) if existing else {}
    cfg["template"] = template
    cfg.setdefault("created_at", date.today().isoformat())
    for k, v in values.items():
        cfg[k] = v
    save_config(project_root, cfg)
    save_state(rtmpl_dir(project_root), State(template_version=manifest.version, hashes=hashes))

    print(
        f"Adopted {project_root} (template {template} @ {manifest.version}); "
        f"{len(hashes)} files baselined"
    )
    return 0

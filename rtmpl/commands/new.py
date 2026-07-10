"""`rtmpl new` — create a new project from a template."""
from __future__ import annotations

from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core.state import State, save_state
from ..core.template import load_manifest, walk_payload
from ..core.tx import atomic_write_bytes
from ._common import (
    CommandError,
    collect_variables,
    config_for_new,
    default_template,
    local_path,
    rtmpl_dir,
    save_config,
)


def _check_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise CommandError(f"target {target} is not empty (use --force to overwrite)")


def run(args) -> int:
    template = args.template or default_template()
    manifest = load_manifest(template)
    flag_values: dict[str, str] = dict(getattr(args, "var", {}) or {})
    name = getattr(args, "name", None)
    if name and manifest.variable_for_field("proj") and "proj" not in flag_values:
        flag_values["proj"] = name
    values = collect_variables(manifest, flag_values, args.no_input)

    target = (
        Path(args.path)
        if getattr(args, "path", None)
        else Path.cwd() / (name or values.get("proj", "project"))
    )
    _check_target(target, getattr(args, "force", False))

    payload = walk_payload(template, manifest)
    rendered = rendermod.render_payload(payload, manifest, values)
    rendermod.check_render_residuals(rendered, manifest)

    target.mkdir(parents=True, exist_ok=True)
    for rel, data in rendered.items():
        atomic_write_bytes(local_path(target, rel), data)

    save_config(target, config_for_new(template, values))
    hashes = {rel: hashmod.hash_data(data) for rel, data in rendered.items()}
    save_state(rtmpl_dir(target), State(template_version=manifest.version, hashes=hashes))

    print(
        f"Created project at {target} "
        f"(template {template} @ {manifest.version}, {len(hashes)} files)"
    )
    return 0

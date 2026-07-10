"""`rtmpl repair` — rebuild ``.rtmpl/state.json`` when it is missing/corrupt.

Repair semantics (vs adopt): a current-template file missing from disk is
recorded as a tombstone (``null``) — conservatively assume the user deleted it,
so the next update does NOT recreate it. Never touches ``config.yaml`` or
business files.
"""
from __future__ import annotations

from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core.state import State, save_state
from ..core.template import load_manifest, walk_payload
from ._common import CommandError, local_path, load_config, rtmpl_dir, values_from_config


def run(args) -> int:
    project_root = Path.cwd()
    cfg = load_config(project_root)
    if not cfg:
        raise CommandError("no .rtmpl/config.yaml — run `rtmpl adopt` first")
    template = cfg.get("template") or getattr(args, "template", None)
    if not template:
        raise CommandError("config.yaml has no template field; pass --template")
    manifest = load_manifest(template)
    values = values_from_config(manifest, cfg)

    rendered = rendermod.render_payload(walk_payload(template, manifest), manifest, values)
    hashes: dict[str, str | None] = {}
    for rel, data in rendered.items():
        if local_path(project_root, rel).exists():
            hashes[rel] = hashmod.hash_data(data)
        else:
            hashes[rel] = None  # tombstone

    save_state(rtmpl_dir(project_root), State(template_version=manifest.version, hashes=hashes))
    print(f"Rebuilt state.json ({template} @ {manifest.version}); {len(hashes)} entries")
    return 0

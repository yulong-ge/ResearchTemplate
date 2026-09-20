"""`rtmpl new` — create a new project from a template."""
from __future__ import annotations

from pathlib import Path

from ..core import hash as hashmod
from ..core import render as rendermod
from ..core.state import MANAGED, OK, SEED_ONLY, State, load_state, save_state
from ..core.template import load_manifest, walk_payload
from ..core.tx import atomic_write_bytes
from ._common import (
    CommandError,
    collect_variables,
    config_for_new,
    default_template,
    local_path,
    ownership_for,
    rtmpl_dir,
    save_config,
)


def _check_target(target: Path, force: bool) -> None:
    if target.exists() and any(target.iterdir()):
        if not force:
            raise CommandError(f"target {target} is not empty (use --force to overwrite)")


def _print_init_guidance(target: Path, guidance) -> None:
    print("\n初始化后的优先顺序：")
    print("先完成下面的记录，再创建第一个实验；Agent 也按这个顺序恢复工作。")
    for index, step in enumerate(guidance, start=1):
        print(f"  {index}. {step.path} — {step.purpose}")
    print(f"\n下一步：cd {target} && rtmpl check && rtmpl resume")


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

    existing_state, existing_status = load_state(rtmpl_dir(target))
    existing_ownership = (
        dict(existing_state.ownership) if existing_state is not None and existing_status == OK else {}
    )

    payload = walk_payload(template, manifest)
    rendered = rendermod.render_payload(payload, manifest, values)
    rendermod.check_render_residuals(rendered, manifest)

    target.mkdir(parents=True, exist_ok=True)
    hashes: dict[str, str | None] = {}
    ownership: dict[str, str] = dict(existing_ownership)
    for rel, data in rendered.items():
        policy = ownership_for(existing_ownership, rel, manifest)
        destination = local_path(target, rel)
        if policy == SEED_ONLY and destination.exists():
            # --force is allowed to refresh template-owned files, but a
            # project-owned research record remains under the project's control.
            hashes[rel] = hashmod.hash_file(destination)[0]
        else:
            atomic_write_bytes(destination, data)
            hashes[rel] = hashmod.hash_data(data)
        ownership[rel] = SEED_ONLY if policy == SEED_ONLY else MANAGED
    for rel, owner in existing_ownership.items():
        if owner == SEED_ONLY and rel not in hashes:
            path = local_path(target, rel)
            if path.exists():
                hashes[rel] = hashmod.hash_file(path)[0]

    save_config(target, config_for_new(template, values))
    save_state(
        rtmpl_dir(target),
        State(template_version=manifest.version, hashes=hashes, ownership=ownership),
    )

    print(
        f"Created project at {target} "
        f"(template {template} @ {manifest.version}, {len(hashes)} files)"
    )
    _print_init_guidance(target, manifest.init_guidance)
    return 0

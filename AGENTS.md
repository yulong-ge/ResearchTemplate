# ResearchKit Framework Development Guide

## Layer Boundary

This repository is the framework/template source, not a live research project.

- Root files are for developing the `rk` framework and the copyable template.
- `templates/ara-research-workspace/` is the project template that users copy to start research work.
- `templates/ara-research-workspace/AGENTS.md` is the consumer-facing agent guide for copied projects.
- Do not mix framework-development instructions into the template-level `AGENTS.md`.

## Start Here

1. Read `docs/adr/0002-batchcom-rk-lite.md` and `docs/plans/2026-06-30-batchcom-rk-lite-design.md` for the accepted current direction.
2. Treat `docs/handoffs/2026-06-30-framework-refactor-handoff.md` as historical context; ADR 0002 and the batchcom RK-lite design supersede any conflicting remote-sync, Mutagen, or runtime-placement guidance there.
3. Read `docs/adr/` before changing repository structure or runtime architecture.
4. Treat `docs/plans/` as framework implementation plans.
5. Treat `templates/ara-research-workspace/docs/` as documentation that will be copied into downstream research projects.

## Framework Direction

- The runtime command is named `rk`.
- `rk` source belongs at the framework repository root, not inside copied project templates.
- Copied projects contain `.rk/project.toml` and use `rk` as an external execution tool.
- The current v1 target is batchcom-specific, Git-first, and RK-lite.
- Do not generalize to multi-remote or Mutagen workflows until a concrete future remote requires it.

## Development Rules

- Use ADRs for architectural decisions.
- Keep framework docs in root `docs/`.
- Keep copyable research workspace files under `templates/ara-research-workspace/`.
- Treat `templates/ara-research-workspace/` as a carefully designed baseline. Before deleting or replacing existing template artifacts, document what they do and ask for confirmation unless the deletion was explicitly approved.
- When replacing obsolete structure, remove the old path directly rather than adding compatibility shims unless compatibility is explicitly requested.
- Prefer small commits after verified framework changes.

## Verification

- Template shell syntax check:
  `bash -n templates/ara-research-workspace/scripts/remote_targets.sh templates/ara-research-workspace/scripts/remote_env.sh templates/ara-research-workspace/scripts/remote_python.sh templates/ara-research-workspace/scripts/remote_sync.sh templates/ara-research-workspace/scripts/remote_preflight.sh`
- Template tests, when Python tests exist:
  `cd templates/ara-research-workspace && uv run pytest tests/`

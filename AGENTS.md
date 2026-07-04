# Skills-Driven ARA Template Framework Guide

## Layer Boundary

This repository is the framework/template source, not a live research project.

- Root files are for maintaining the copyable research workspace template.
- `templates/ara-research-workspace/` is the project template that users copy to start research work.
- `templates/ara-research-workspace/AGENTS.md` is the consumer-facing agent guide for copied projects.
- Do not mix framework-development instructions into the template-level `AGENTS.md`.

## Start Here

1. Read `docs/adr/0001-framework-template-split.md` for the framework/template split.
2. Read `docs/plans/2026-06-30-repository-layout-restructure.md` for the layout-only refactor plan.
3. Treat `templates/ara-research-workspace/docs/` as documentation that will be copied into downstream research projects.

## Framework Direction

- This repository currently owns a copyable research workspace template only.
- There is no framework runtime tool in this repository.
- Do not add runtime, scheduler, manifest, Mutagen, or multi-remote platform features until a concrete future design is accepted.
- Keep `templates/ara-research-workspace/` as a carefully designed baseline.

## Development Rules

- Use ADRs for architectural decisions.
- Keep framework docs in root `docs/`.
- Keep copyable research workspace files under `templates/ara-research-workspace/`.
- Before deleting or replacing existing template artifacts, document what they do and ask for confirmation unless the deletion was explicitly approved.
- When replacing obsolete structure, remove the old path directly rather than adding compatibility shims unless compatibility is explicitly requested.
- Prefer small commits after verified framework changes.

## Verification

- Template shell syntax check:
  `bash -n templates/ara-research-workspace/scripts/remote_targets.sh templates/ara-research-workspace/scripts/remote_env.sh templates/ara-research-workspace/scripts/remote_python.sh templates/ara-research-workspace/scripts/remote_sync.sh templates/ara-research-workspace/scripts/remote_preflight.sh`
- Template tests, when Python tests exist:
  `cd templates/ara-research-workspace && uv run pytest tests/`

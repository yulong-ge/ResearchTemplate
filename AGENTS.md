# BatchCom Research Template Framework Guide

## Layer Boundary

This repository is the framework/template source, not a live research project.

- Root files are for maintaining the copyable BatchCom research template.
- `templates/batchcom-research-template/` is the project template that users copy to start research work.
- `templates/batchcom-research-template/AGENTS.md` is the consumer-facing agent guide for copied projects.
- Do not mix framework-development instructions into the template-level `AGENTS.md`.

## Start Here

1. Read `docs/adr/0001-framework-template-split.md` for the framework/template split.
2. Read `docs/plans/2026-06-30-repository-layout-restructure.md` for the layout-only refactor plan.
3. Treat `templates/batchcom-research-template/docs/` as documentation that will be copied into downstream research projects.

## Framework Direction

- This repository currently owns a copyable BatchCom research project template only.
- There is no framework runtime tool in this repository.
- Do not add runtime, scheduler, manifest, file-sync daemon, or multi-remote platform features until a concrete future design is accepted.
- Keep `templates/batchcom-research-template/` as a carefully designed baseline.
- The template is Git-first: Mac local work and BatchCom server-local work synchronize through the same Git repository.

## Development Rules

- Use ADRs for architectural decisions.
- Keep framework docs in root `docs/`.
- Keep copyable research workspace files under `templates/batchcom-research-template/`.
- Before deleting or replacing existing template artifacts, document what they do and ask for confirmation unless the deletion was explicitly approved.
- When replacing obsolete structure, remove the old path directly rather than adding compatibility shims unless compatibility is explicitly requested.
- Prefer small commits after verified framework changes.

## Verification

- Template shell syntax check:
  `bash -n templates/batchcom-research-template/scripts/remote_targets.sh templates/batchcom-research-template/scripts/remote_env.sh templates/batchcom-research-template/scripts/remote_python.sh templates/batchcom-research-template/scripts/remote_sync.sh templates/batchcom-research-template/scripts/remote_preflight.sh templates/batchcom-research-template/scripts/remote_run.sh`
- Template tests, when Python tests exist:
  `cd templates/batchcom-research-template && uv run pytest tests/`

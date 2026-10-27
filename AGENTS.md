# BatchCom Research Template Framework Guide

This repository maintains the framework and copyable template source.

- Root code and `docs/` maintain the `rtmpl` CLI and its decisions.
- `rtmpl/templates/batchcom-research/` is the consumer-facing project template.
- Keep framework-development rules here and research-workspace rules in the template's `AGENTS.md`.

## Framework direction

`rtmpl` creates and updates Git-first research projects. It owns template lifecycle commands and
hash-protected file updates; generated projects use human-written Plans to define experiment
execution and storage workflows.

The template contains ordinary human notes, Plans, and experiment output directories. The CLI does
not model research objects, automation modes, or note ownership. Existing natural-language
research files are migrated manually after applying a newer template.

## Development rules

- Use ADRs for architectural decisions and keep them in `docs/adr/`.
- Keep copyable workspace files below `rtmpl/templates/batchcom-research/`.
- Remove obsolete paths directly unless compatibility is explicitly requested.
- Preserve unrelated working-tree changes and make small verified commits.
- Run Python and tests with `uv`.

## Verification

Run `uv run pytest` before delivery. For template changes, exercise `rtmpl list`, scaffold a
disposable project with `rtmpl new`, and verify `rtmpl status` plus update protection for
user-edited managed files.

- Run template validation from the repository root. Running `uv` inside a template directory can select that template's `pyproject.toml` instead of the framework environment.
- If the default uv cache is not writable, use `UV_CACHE_DIR=/private/tmp/researchtemplate-uv-cache uv run --no-sync pytest -q` with the existing project environment. A cache-permission error is not a test result.

## Template maintenance boundaries

- Reusable research logic, parsing, and result code belong in generated `src/`; human-facing command orchestration belongs in `scripts/`, and implementation helpers in `scripts/internal/`.
- The research template supplies no default smoke/check phase or entrypoint. Add one only for an explicitly requested workflow.
- When adding third-party capabilities, distinguish this framework from generated projects. Include only the requested skill directories and their installation guidance; do not install a tool CLI into the template repository or copy unrelated upstream material.
- A request to disable an `opencode.json` entry does not authorize deleting it or unrelated configured entries.
- Verify referenced paths and upstream structure before designing changes. Deleted paths and retired ADRs are not current design evidence.

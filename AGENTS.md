# BatchCom Research Template Framework Guide

This repository maintains the framework and copyable template source.

- Root code and `docs/` maintain the `rtmpl` CLI and its decisions.
- `rtmpl/templates/batchcom-research/` is the consumer-facing project template.
- Keep framework-development rules here and research-workspace rules in the template's `AGENTS.md`.

## Framework direction

`rtmpl` creates and updates Git-first research projects. It owns template lifecycle commands and hash-protected file updates; generated projects define experiment execution and storage workflows.

The template uses evidence-traceable records with configurable human or automatic Inner and Outer Loops. Seed-only research records remain project-owned after scaffolding and are never overwritten by template updates, including `--force`. Natural-language record migration is intentionally manual after applying a newer template.

## Development rules

- Use ADRs for architectural decisions and keep them in `docs/adr/`.
- Keep copyable workspace files below `rtmpl/templates/batchcom-research/`.
- Remove obsolete paths directly unless compatibility is explicitly requested.
- Preserve unrelated working-tree changes and make small verified commits.
- Run Python and tests with `uv`.

## Verification

Run `uv run pytest` before delivery. For template changes, exercise `rtmpl list`, scaffold a disposable project with `rtmpl new`, and verify `rtmpl status` plus seed-only protection on update.

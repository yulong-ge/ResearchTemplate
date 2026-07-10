---
name: rtmpl
description: Use when scaffolding a new research project from a managed template, syncing template improvements into an existing project without clobbering user edits, bringing a legacy cp-created project under management, or checking what template changes are pending
---

# rtmpl — research template sync

## Overview
`rtmpl` manages research-project templates: create (`new`), sync improvements (`update`), bring legacy `cp` projects under management (`adopt`). It hash-tracks template files so user edits are never silently clobbered; Markdown merges are surfaced for review, never auto-applied. Install once: `uv tool install git+<rtmpl-repo>`.

## When to Use
- Starting a new research project → `rtmpl new`
- The template improved and you want to pull changes into an existing project → `rtmpl update`
- A project was created by `cp -R` (no `.rtmpl/`) and needs to come under management → `rtmpl adopt`
- "What would update change?" / pre-flight check → `rtmpl status` (= `update --dry-run`)
- `.rtmpl/state.json` is missing/corrupt → `rtmpl repair`

## Commands (run `rtmpl <cmd> --help` for full flags)
| Command | Purpose |
|---|---|
| `new <proj>` | scaffold a project (renders placeholders, writes `.rtmpl/`) |
| `update` | apply template changes; prompts on user-edited files |
| `adopt` | baseline an existing project (no business-file changes) |
| `status` | show pending changes, write nothing |
| `repair` | rebuild `.rtmpl/state.json` from disk |
| `list` | show available templates |

Key flags: `--no-input` (agent/non-interactive), `--var field=value` (repeatable), `--force`/`--skip` (resolve all changed files), `--dry-run`, `--allow-downgrade`.

## Key Concepts
- **managed** = files present in the template tree. User-added files (`research/runs/*`, `paper/*`, your `src/` code) are never touched.
- **hash protection**: editing a managed file → it shows as `changed` on update → you decide per file: `overwrite` / `skip` / `create-new` (parks the template version as `<file>.new`).
- **Markdown is never auto-merged** — review the `.new` copy (or let the agent merge it), then delete it. `.new` is collision-safe (`.new.1`, `.new.2`…).
- **single state**: `.rtmpl/state.json` (template_version + hashes); `.rtmpl/config.yaml` (your project values like `proj`, `conda_env`).
- **version skew**: updating an older-project with a newer tool is forward; a newer-project with an older tool aborts unless `--allow-downgrade`.

## Common Mistakes
- Using `cp -R` to start a project → use `rtmpl new` (gets placeholder rendering + hash tracking).
- Editing a managed file and expecting silent auto-update → update will **prompt**; unresolved prompts under `--no-input` abort before any write (use `--force`/`--skip`).
- A legacy `cp` project without `.rtmpl/` → run `rtmpl adopt` first. Adopt baselines on the *template* hash, so customized files become `changed` (prompted), never auto-clobbered.
- Missing/corrupt `state.json` → `rtmpl repair` rebuilds it (a file missing on disk becomes a tombstone, so it is NOT recreated).

## Non-interactive (agent) pattern
```
rtmpl new myproj --var conda_env=ml --var zotero_api_key=<key> --no-input
cd myproj && rtmpl status        # see pending
rtmpl update --force             # or --skip; aborts if changed files need a decision
```

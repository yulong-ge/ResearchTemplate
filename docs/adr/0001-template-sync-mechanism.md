# ADR-0001: Template → project sync mechanism

- Status: **Superseded by [ADR-0002](0002-rtmpl-sync-framework.md)**
- Date: 2026-07-07
- Supersedes: none

## Context

`templates/batchcom-research-template/` is the copyable upstream. Downstream research projects (e.g. `diffusion-neural-operator`) are created by copying it and customizing:

- placeholders filled: `<proj>` / `<conda-env>` in `src/paths.py` and `pyproject.toml`
- research content added: `research/*.md`, `research/runs/*`, `literature/notes/*`, code under `src/`
- repo wired to its own GitHub remote + credentials

When the upstream template improves, those changes must reach already-created downstream projects **without clobbering user-edited files**. Two structural constraints shape the choice:

1. The template is nested in the framework repo (`templates/...`), not its own repo — so `git clone` of "just the template" is not directly possible, and downstream `cp` copies share **no git history** with the template.
2. Downstream projects diverge immediately (placeholders filled, content added), so any sync must distinguish template-managed files from user-owned files.

## Decision

**For now: keep `cp`-based creation.** Complexity is low, the template is stable, and the number of downstream projects is small. Re-syncing template improvements into an existing project is done manually (diff + apply the specific changed template files, skipping the project's filled values).

**Deferred: a config-driven framework with a non-clobbering `update` command**, to be built once `cp`-based manual sync becomes painful. The design is recorded below so the idea is not lost.

## Deferred design (the idea to preserve)

Modeled on `~/code/trellis-research-template`, which already implements this pattern: it also creates projects with `cp -R`, and uses a hash file to make later updates safe.

### Mechanism: track applied state, skip user-edited files

- A **config file** (e.g. `.batchcom/config.yaml`) holds `proj`, `conda_env`, `git_remote`, … — replacing the `<proj>` / `<conda-env>` placeholders. Template files become renderable (`{{proj}}`, `{{conda_env}}`).
- A **hash file** (e.g. `.batchcom/.template-hashes.json`) records the SHA256 of every template-managed file **at last apply**, plus a `.version`.
- On `update`, for each managed file:
  - current hash == recorded hash → user did not touch it → safe to re-render from the new template + config.
  - current hash != recorded hash → user edited it → **skip + warn** (or 3-way merge).
  - files never in the hash table (user-owned) → never touched.

### File classification

| Class | Examples | On `update` |
|---|---|---|
| Managed (template-owned) | `AGENTS.md`, `README.md`, `.agents/skills/research-record/`, `.opencode/agents/remote-exec.md`, `.opencode/opencode.json`, `.gitignore`, `docs/plans/README.md`, `src/__init__.py`, research-file *skeletons* | re-render if unedited; skip if user edited |
| Generated from config (do not hand-edit) | `src/paths.py`, `pyproject.toml` | always regenerate from config (warn if user hand-edited) |
| User-owned (never touched) | `research/runs/*`, filled `research/*.md` content, `literature/notes/*`, `paper/`, `src/<code>`, `data/` | never touch |

### Commands

- `new <name>` — copy template → render from config → `git init` → (optional) create remote + push.
- `update` — re-apply template using the hash table; regenerate config-driven files.

### Two implementation paths (pick when we build it)

- **A. copier (recommended, least code).** Convert the template to a copier template (`{{proj}}` Jinja + `copier.yml`). `copier copy` scaffolds; downstream gets `.copier-answers.yaml`; `copier update` does 3-way merge preserving user edits. Near-zero custom code.
- **B. custom trellis-style CLI.** `.batchcom/config.yaml` + `.template-hashes.json` + `new`/`update` Python scripts. More control, ~300 lines to maintain.

## Consequences

- **Now:** no extra tooling; sync is manual and acceptable at current scale. Risk: a manual sync can miss a file or clobber a filled value if done carelessly — mitigated by the file-classification table above as a checklist.
- **Trigger to build the framework:** when (a) ≥3 downstream projects exist, or (b) template changes start touching many files at once, or (c) a manual sync ever clobbers user content. At that point, build path A (copier) first; fall back to B only if copier's merge semantics are insufficient.
- **Migration note:** existing `cp`-created projects (e.g. `diffusion-neural-operator`) have no hash table / shared history, so they cannot cleanly `update` from a future framework on day one — they'd be migrated by re-scaffolding from the framework and copying their user-owned files over.

## References

- `~/code/trellis-research-template` — reference implementation of the hash-tracked update pattern (`.trellis/.template-hashes.json`, `.trellis/.version`, `.trellis/config.yaml`, `.trellis/scripts/`).
- `docs/plans/2026-07-07-template-refactor.md` — the template refactor that motivated this question.
- copier: https://copier.readthedocs.io (scaffold + `copier update` with 3-way merge).

# ADR-0002: rtmpl — template sync framework

- Status: **Accepted**
- Date: 2026-07-09
- Supersedes: [ADR-0001](0001-template-sync-mechanism.md)

## Context

ADR-0001 deferred a template-sync framework and recorded only a sketch. Since then:

- The template went through a large refactor (`docs/plans/2026-07-07-template-refactor.md`, 10 actions).
- A downstream project (`diffusion-neural-operator`) was created via `cp` and has already needed one manual upstream-sync commit — during which a GitHub PAT leaked into its remote URL. Manual sync is already happening and already risky.
- We studied the real upstream reference, **trellis v0.6.6** (`github.com/mindfold-ai/trellis`), by cloning and reading its source — not the stale local assumptions ADR-0001 was based on.

The trigger conditions ADR-0001 set for building the framework (multi-file template churn; manual sync already occurring and already clobbering/leaking) are met. We now build it, modeled on trellis's verified design.

### Correction to ADR-0001's reference

ADR-0001 cited trellis as a ready hash-tracked-update implementation for a research template. Source inspection shows that is inaccurate: trellis's `.template-hashes.json` is written by the external `trellis` CLI (npm package) to track **its own runtime files** (`.trellis/` + per-platform agent config), and the research-template repo itself still relies on manual re-merge. trellis's value to us is the **mechanism** (hash + 5-state + 3-option conflict + backup), which we re-implement for our own template — not a drop-in reuse.

## Decision

Build **`rtmpl`**, a Python CLI that manages research-project templates: create (`new`), sync template improvements into existing projects (`update`), adopt legacy `cp` projects (`adopt`).

### D1 — Implementation language: Python

- The project's golden rule is `uv` for all Python; the template's content is Python (`paths.py`, `pyproject.toml`). A scaffolding tool written in Python adds **zero new runtime** (reuses `uv tool install`), is isomorphic with the template, and is at home on the BatchCom server (conda + uv already present).
- trellis's value is its design, not its TypeScript code — its core logic (hash / 5-state / prompt) is language-neutral and rewrites cleanly in ~500 lines of stdlib Python.

### D2 — Distribution: in-repo Python package, global CLI

- `rtmpl` lives as a package **inside the framework repo** alongside the templates. Installed once via `uv tool install git+<github-repo>`, exposing a global `rtmpl` command. Development: `uv run rtmpl` (equivalent, no conflict with the install path).
- The tool is **not** distributed with each downstream project (avoids a meta-sync problem where the tool itself would need syncing). Downstream projects carry only `.rtmpl/` state files.

### D3 — Template access: in-package (A1)

- Templates ship **inside the package** as data (`rtmpl/templates/<name>/`). Located via `importlib.resources.files("rtmpl") / "templates"` — one expression that resolves to the local source tree during development and to the packaged wheel in production.
- No per-`update` network clone: the tool and templates share one repo, one version. Upgrading templates = `uv tool upgrade rtmpl`.

### D4 — Multi-template aware

- `rtmpl/templates/` may hold several templates (`batchcom-research/`, future `<other-server>-research/`). Each has a `template.yaml` manifest. The command name (`rtmpl`) is platform-neutral; adding a server template = adding a directory + manifest, zero tool-code change.

### D5 — File model: implicit managed, no classification

- A file is **managed** iff it exists in the template tree (walk all). Files not in the template (user-added `research/runs/*`, `paper/*`, `src/model.py`) are never touched.
- **Update's managed universe** = `current_template_paths ∪ recorded_paths` (the union is what lets `orphanedManaged` detect removed-from-template files). User-owned = outside both.
- **No** static/scaffold split, **no** protected list, **no** managed-block markers. Hash tracking uniformly protects every user modification: edit a managed file → its hash changes → it falls into the `changed` state → user decides.

### D6 — Sync mechanism: total hash classifier + 3-option conflict + transactional single-file commit (per trellis)

- State lives in `.rtmpl/state.json` = `{schema, template_version, hashes}` where `hashes[path]` is a hex sha256 or `null` (tombstone for a user-deleted managed file). Text files hash CRLF→LF-normalized content; binary files (NUL/non-UTF-8) hash raw bytes and are never rendered. (Not trellis's separate `.template-hashes.json` + `.version` — folded into one mutable file for atomicity.)
- Update's managed universe = `current_template_paths ∪ recorded_paths`; the classifier is **total** (8 rows) over `(inTmpl, onDisk, disk==template, recorded)`, covering `unchanged / autoUpdate / new / changed / userDeleted / orphanedManaged / deadOrphan` — including every `recorded=null` (tombstone) combination and a state-heal that clears a tombstone when the file returns equal to template. Path keys are validated on load (POSIX-relative, no `..`/absolute/`.rtmpl`/`.git`).
- `changed`/`orphanedManaged` resolution: `overwrite` / `skip` / `create-new`(`<file>.new`) + apply-to-all; non-interactive via `--force` / `--skip` / `--no-input` (unresolved prompts abort before backup).
- Transactional: per-file temp + atomic `os.replace`; `.lock` + `.pending`; `state.json` committed as a single atomic replace after all business writes (`config.yaml` is read-only during update except a documented default-variable backfill); backup of the full universe + `manifest.json` happens only after confirmation, immediately before the first write (so `--dry-run`/`status` write nothing); interrupted runs detected via `.pending` → manual restore from backup.
- **No line-level merge.** Verified trellis has zero diff/merge code (`grep` of `src/`) — it gives 3 options and leaves prose merging to the user. We do the same; Markdown fine-merging is delegated to the opencode agent against the `.new` material.

### D7 — Placeholders: literal substitution

- Two placeholders (`<proj>`, `<conda-env>`) replaced **literally** (not Jinja — the template contains real `{{ }}` in LaTeX/f-strings/bibtex that Jinja would corrupt). Substitution scoped to `render_files` per variable. Hash computed on **rendered** content.

### D8 — Non-interactive first

- All write commands (`new`/`update`/`adopt`) support `--no-input` + `--var k=v`. A missing required variable under `--no-input` fails fast (no guessed defaults). The agent drives via flags; humans via prompts — same logic.

### D9 — Repo host: GitHub (not Gitee)

- Overrides the Gitee decision in `2026-07-07-template-refactor.md` D2. Rationale: GitHub's finer-grained access control.

### D10 — Dependencies: stdlib + PyYAML only

- argparse (CLI), `input()` (prompts), `hashlib`/`pathlib`/`json` (stdlib). Sole runtime dependency: **PyYAML** (read `template.yaml` / `config.yaml`).

## Refinements from cross-review (rounds 1–3)

Two codex cross-model review rounds (12 + 9 findings, all adopted). Design-relevant outcomes:

- **Adopt semantics (round 1 BLOCKER).** `adopt` records the **rendered current-template hash** per disk-present file (matching trellis `init`), NOT the disk hash — otherwise `autoUpdate` would auto-clobber every legacy-customized file. Customized files → `changed` (prompt); **round 2**: template files missing on disk are NOT tombstoned at adopt (they may be later template additions) → first `update` classifies them `new`.
- **Single mutable state file (round 2).** All `update`-mutable state — `template_version` + hashes — lives in **`.rtmpl/state.json`**, committed by ONE atomic `os.replace`. `config.yaml` holds only vars/template/created_at and is read-only during `update`. (Round 1's "version in config.yaml" was abandoned: two files cannot be atomically committed together.) Deleted managed files are tombstones (`hashes[path] = null`).
- **`orphanedManaged` state (round 1) + universe (round 2).** Removed-from-template files no longer linger; update's universe is `current_template_paths ∪ recorded_paths`. Pristine orphans → safe-delete prompt; modified → preserved; dead orphans (not in template, not on disk) pruned.
- **Transactionality (round 1 + 2).** per-file temp+atomic replace; `.lock` against concurrent runs; `.pending` marker for interrupt detection; backup covers the full write/delete universe (template ∪ recorded); `--dry-run`/`status` write nothing.
- **Binary-safe hashing (round 1).** raw-byte SHA256 for non-text files (PDFs), never rendered.
- **Hash-file health gate (round 1 + 2).** `load_state→(state,status)`; only `update`/`status` require `ok` — `missing` → run `new`/`adopt`; `corrupt`/`unsupported`/`version_unknown` → run `repair`. `new`/`adopt` create state from missing (the round-2 fix to a round-1 over-block). `repair` rebuilds `state.json` (incl. version); never edits `config.yaml`/business files.
- **Variable validation (round 1).** regex validation, residual-token + count checks, deterministic order — prevents TOML/Python-literal injection and replacement collisions.
- **Walker hygiene (round 1).** manifest (`template.yaml`) + `__pycache__`/`*.pyc`/`*.DS_Store` hard-excluded.
- **`new` target guard (round 1).** destination must be absent or empty (`--force` to overwrite).
- **`.gitignore` (round 1).** rtmpl internals (`.backup-*`, `.lock`, `.pending`, `*.tmp`, `*.new`) ignored; `config.yaml` + `state.json` tracked.
- **Total classifier + tombstone lifecycle (round 3).** the classifier is total (8 rows) over `current_template ∪ recorded`, covering every `recorded=null` (tombstone) case; tombstones clear when a file returns equal to template; dead orphans pruned. Round-2's non-total classifier was the round-3 BLOCKER.
- **adopt vs repair split (round 3).** adopt (no reliable history) leaves missing template files unrecorded → first update `new`; repair (existing project, damaged state) tombstones them → no recreate. Keeps repair idempotent and preserves user-deletion knowledge.
- **equal-version still classifies (round 3).** equal version is not a no-op — drift/tombstone/orphan/untracked are still detected; `--force` only governs `changed`/orphan resolution, not whether classification runs.
- **Backup manifest + path-key safety (round 3).** backup writes `manifest.json` (full universe + per-path pre-run state + planned action) so manual restore can delete newly-created files; `load_state` rejects unsafe path keys (absolute, `..`, `.rtmpl`/`.git`, non-POSIX) → status `corrupt`.

Full detail, the 8-row classifier, and the state-transition table live in `docs/plans/2026-07-09-rtmpl-framework.md`.

## Alternatives considered

| Alternative | Rejected because |
|---|---|
| **copier** (Jinja scaffolder + 3-way merge) | Template contains real `{{ }}` (LaTeX `math_commands.tex`, Python f-strings, bibtex) that global Jinja rendering corrupts; only 3 files even need rendering — disproportionate. |
| **Reuse trellis's official template mechanism** | trellis's registry/marketplace serves only `.trellis/spec/` (`template-fetcher.ts` hardcodes `spec: ".trellis/spec"`); it cannot manage `AGENTS.md`/`paths.py`/`pyproject.toml`/`research/`, and would drag in trellis's whole task/session runtime, contradicting the human-collaborative direction. |
| **TypeScript / npm** | Would impose node on a pure deep-learning workflow that already standardizes on `uv`; the tool is a scaffold, not an agent harness, so TS's agent-ecosystem advantage is unused. |
| **Gitee** | Coarser access control than GitHub (D9). |
| **Per-`update` git clone of the framework repo (A2)** | Tool and templates share one repo → they always move in lockstep; cloning on every update is redundant overhead with no real decoupling. In-package (A1) is simpler and offline. |
| **static/scaffold file classification** | Unnecessary; hash tracking uniformly handles "user edited it" for every file. Adds complexity with no benefit. |
| **managed-block markers** | Our Markdown is "whole-file user-participated", not "clearly partitioned regions" — markers don't fit. trellis uses them for its own partitioned files; we have none. |
| **3-way line merge** | Unreliable for Markdown prose (git itself conflicts often); trellis deliberately omits it. `.new` + agent is the honest answer. |

## Consequences

- One package (`rtmpl`) to maintain (~500 lines stdlib + PyYAML). Templates and tool version together.
- Downstream projects stay clean: only small `.rtmpl/` state files, no tool code.
- Existing `cp`-created projects (`diffusion-neural-operator`) migrate via `rtmpl adopt`, which records the **rendered template hash** as baseline (not the disk content) — so the first `update` prompts on every legacy deviation instead of auto-clobbering it.
- Markdown merges remain a human/agent task by design — the tool detects and surfaces, never auto-merges prose.
- ADR-0001 is superseded in full.

## References

- Upstream reference (mechanism only, not code reuse): `github.com/mindfold-ai/trellis` v0.6.6 — `packages/cli/src/utils/template-hash.ts`, `packages/cli/src/commands/update.ts`.
- Implementation plan: `docs/plans/2026-07-09-rtmpl-framework.md`.
- Superseded: `docs/adr/0001-template-sync-mechanism.md`.

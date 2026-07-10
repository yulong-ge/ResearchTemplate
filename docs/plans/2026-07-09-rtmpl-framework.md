# Plan: rtmpl template sync framework

- Date: 2026-07-09
- Revised: 2026-07-09 (codex cross-review: round 1 = 12 findings, round 2 = 9, round 3 = 8 — all adopted)
- Status: Approved (design grilled + cross-reviewed x3)
- Scope: new `rtmpl` Python package + relocate template + `template.yaml` manifest
- Decision record: `docs/adr/0002-rtmpl-sync-framework.md`

## 1. Background

The framework repo owns a copyable research template. Downstream projects are created by copying it; when the template improves, those changes must reach existing projects **without clobbering user edits**. Manual sync is already happening and already leaked a credential once. ADR-0002 decides to build `rtmpl`, modeled on trellis v0.6.6's verified mechanism (hash + state classification + 3-option conflict + backup), re-implemented in Python. Three codex cross-review rounds progressively hardened the state model: a single mutable `state.json`, a total classifier over `current_template ∪ recorded`, tombstone lifecycle, transactional single-file commit, and path-key safety.

## 2. Resolved Decisions

| # | Branch | Decision |
|---|---|---|
| D1 | Language | **Python** (uv golden rule; zero new runtime) |
| D2 | Distribution | **In-repo package, global CLI** (`uv tool install git+<repo>`; `uv run` dev-equivalent); not distributed per-project |
| D3 | Template access | **In-package** (`rtmpl/templates/`), `importlib.resources`, dev/prod unified |
| D4 | Multi-template | `rtmpl/templates/<name>/` + per-template `template.yaml`; neutral command name |
| D5 | File model | **Implicit managed**; update universe = `current_template_paths ∪ recorded_paths`; user-owned = outside both. No classification/protected/managed-block. |
| D6 | Sync | total hash classifier + 3-option conflict + pre-mutation backup; **no line merge** |
| D7 | Placeholders | literal substitution + regex validation + residual-token check (not Jinja) |
| D8 | Interaction | non-interactive first (`--no-input`) on all write commands; unresolved prompts abort unless `--force`/`--skip` |
| D9 | Repo host | **GitHub** |
| D10 | Dependencies | stdlib + **PyYAML** only |
| D11 | Removed template files | **`orphanedManaged`** via universe union; pristine → safe-delete prompt, modified → preserve, dead → prune |
| D12 | State authority | **Single mutable file** `.rtmpl/state.json` (`template_version` + `hashes`, `null`=tombstone); one atomic replace per `update`. `config.yaml` = vars only (new/adopt write; read-only in `update` except the one documented default-var backfill, §3.1). |
| D13 | Transactionality | per-file temp+`os.replace`; `.lock`; `.pending`; state.json committed last; interrupt → restore from backup |
| D14 | Binary files | raw-byte SHA256, no normalize/render (NUL/non-UTF-8) |
| D15 | State health | `load_state→(state,status)`; `update`/`status` require `ok`; `new`/`adopt` create from missing; corrupt/unsupported/version_unknown → `repair`. **Path-key safety**: reject non-POSIX/absolute/`..`/empty/`.rtmpl`/`.git` keys. |
| D16 | Tombstones | deleted managed file = `hashes[path]=null`. Lifecycle closed by the total classifier (§5). |

Rejected: copier, reuse trellis, TypeScript, per-update clone, static/scaffold split, managed-block, 3-way merge. See ADR-0002 §Alternatives.

## 3. Data Model

### 3.1 `template.yaml` (template source only; downstream does NOT carry it)

```yaml
# rtmpl/templates/batchcom-research/template.yaml
name: batchcom-research
display: "BatchCom 深度学习研究模板"
version: "0.1.0"
variables:
  - token: "<proj>"
    field: proj
    render_files: ["pyproject.toml", "src/paths.py"]
    prompt: "项目 slug（如 my-research）"
    required: true
    validation: '^[a-z0-9][a-z0-9-]*$'
  - token: "<conda-env>"
    field: conda_env
    render_files: ["src/paths.py"]
    prompt: "服务器 conda 环境名（如 ml）"
    required: true
    validation: '^[A-Za-z0-9_.-]+$'
# Walker hard-excludes (non-overridable): template.yaml, __pycache__/, *.pyc, *.pyo, .DS_Store
exclude: []
```

- `validation` runs at collection; failure fatal.
- After render, each render_file is checked for residual tokens + expected counts; binary files rejected from `render_files`.
- **New variables across template versions**: a variable may carry `default: ...`. If a future template version adds a variable that already has a `default`, `update` backfills it into `config.yaml` during the pre-commit prep step (the *only* `update` write to `config.yaml`). A new **required** variable without a default cannot be silently satisfied — bump the template `name` or re-run `adopt` to collect it. This keeps the single-mutable-file invariant intact for the common case.

### 3.2 Downstream `.rtmpl/`

```
.rtmpl/
├── config.yaml     # template / created_at / variable values   (new/adopt write; update read-only except default backfill)
├── state.json      # schema / template_version / hashes        ← THE mutable transaction file (atomic replace)
├── .lock           # advisory lock (during a write run)
└── .pending        # transaction-in-progress marker (mid-update)
```

`config.yaml`:
```yaml
template: batchcom-research
created_at: 2026-07-09
proj: my-research
conda_env: ml
```

`state.json`:
```json
{ "schema": 2, "template_version": "0.1.0",
  "hashes": { "AGENTS.md": "sha256...", "research/runs/.gitkeep": null } }
```
`hashes[path]` = hex sha256, or `null` (tombstone). **Path keys are validated on load** (D15): must be POSIX relative, no leading `/`, no `..`, no empty/control segments, and must resolve strictly under the project root while excluding `.rtmpl/**` and `.git/**`. Unsafe keys → status `corrupt`.

`config.yaml` + `state.json` git-tracked; `.lock`/`.pending`/`.backup-*/` gitignored (§12).

### 3.3 Text vs binary hashing

- **Text** (UTF-8, no NUL): SHA256 of CRLF→LF-normalized content.
- **Binary** (NUL/non-UTF-8): raw-byte SHA256, no normalize, never rendered.

### 3.4 Version authority & skew

`template_version` lives only in `state.json`. `update` compares installed tool template `version` vs project's:

| Installed vs project | Action |
|---|---|
| newer | proceed |
| equal | **still classify** (drift/tombstone/orphan/untracked can exist at equal version); report "up-to-date" only if no actionable states. `--force` does NOT bypass this — it only governs `changed`/orphan resolution. |
| older | **abort** unless `--allow-downgrade` |
| missing/unparseable | **abort** → `rtmpl repair` |

## 4. Commands

| Command | Interface | Behavior |
|---|---|---|
| `list` | `rtmpl list` | enumerate templates |
| `new` | `rtmpl new <proj> [--template T] [--path P] [--var k=v]... [--no-input]` | target absent/empty (else error; `--force`). validate+render → write files → write `config.yaml`+`state.json` |
| `update` | `rtmpl update [--force\|--skip\|--allow-downgrade\|--dry-run\|--no-input]` | flow below |
| `adopt` | `rtmpl adopt [--template T] [--var k=v]... [--no-input] [--repair]` | no business writes; write `config.yaml`+`state.json` (adopts semantics §5); `--repair` overwrites corrupt existing state |
| `status` | `rtmpl status` | = `update --dry-run` |
| `repair` | `rtmpl repair` | rebuild `state.json` (repair semantics §8); never touches `config.yaml`/business files |

### `update` flow

```
 1. acquire .rtmpl/.lock (abort if held)
 2. load config + state.json (health: ok|missing|corrupt|unsupported|version_unknown)
       ok → proceed
       missing → abort: "run rtmpl new/adopt"
       corrupt|unsupported|version_unknown → abort: "run rtmpl repair"
 3. skew check (§3.4); abort on downgrade w/o --allow-downgrade
 4. universe = current_template_paths ∪ recorded_paths
 5. classify each universe path (§5 — total, 8 rows)
 6. PRINT REPORT
 7. if --dry-run / status: release lock, exit (NO backup, NO writes)
 8. resolve changed/orphanedManaged prompts (interactive | --force/--skip | --no-input→abort if unresolved)
 9. BACKUP: snapshot every disk-present universe path → .backup-<ts>/ AND write manifest.json
       (manifest = full universe + per-path pre-run present/absent + hash + planned action, so a
        manual restore knows which newly-created files to delete)          ← first mutation
10. write .pending
11. apply BUSINESS mutations (write/delete files) via temp + atomic os.replace
12. backfill new default-variables into config.yaml if any (only update write to config)
13. commit state.json: apply STATE mutations (§6) + bump template_version → single atomic os.replace
14. remove .pending; release lock
```

## 5. Classifier (total — 8 rows over the universe)

Notation: `inTmpl` = path ∈ current_template; `onDisk` = file exists; `disk==tmpl` = byte-equal to rendered template; `rec` = recorded entry (`<hash>` | `null` tombstone | absent).

| # | inTmpl | onDisk | disk==tmpl | rec | State | Action |
|---|---|---|---|---|---|---|
| 1 | Y | Y | Y | any | `unchanged` | skip; **state-heal**: ensure `rec=hash(tmpl)` (clears a stale tombstone `null`, or records an untracked file) |
| 2 | Y | Y | N | `==hash(disk)` | `autoUpdate` | business: write tmpl |
| 3 | Y | Y | N | `≠hash(disk)` (`null`/absent/other) | `changed` | prompt overwrite/skip/create-new |
| 4 | Y | N | — | absent | `new` | business: write tmpl |
| 5 | Y | N | — | `<hash>` or `null` | `userDeleted` | preserve deletion; state: set `rec=null` (tombstone; don't recreate) |
| 6 | N | Y | N (always) | `==hash(disk)` | `orphanedManaged` (pristine) | prompt safe-delete |
| 7 | N | Y | — | `≠hash(disk)` or `null` | `orphanedManaged` (modified) | preserve + report |
| 8 | N | N | — | any | `deadOrphan` | state: prune entry |

Rows are mutually exclusive and cover every `(inTmpl, onDisk, disk==tmpl, rec)` combination — the tombstone holes round 3 flagged (`rec=null` in each quadrant) now resolve: row1 clears a tombstone when the file returns equal to template; row5 keeps `null` for a deleted template-file; row7 treats a `null`-but-on-disk orphan as modified; row8 prunes a `null` dead orphan.

### adopt vs repair semantics (differ on what they write, and on "inTmpl & !onDisk")

**adopt** writes `config.yaml` + `state.json`; **repair** writes only `state.json` (never `config.yaml` or business files). Both record `hash(rendered template)` for disk-present managed files. They differ on a current-template file **missing from disk**:

- **adopt** (first-time bring-in, no reliable history): record **nothing** → first `update` classifies it `new` (likely a template addition since the `cp`).
- **repair** (existing project, state damaged): record **`null` tombstone** → conservatively assume the user deleted it; first `update` classifies `userDeleted` and does NOT recreate. This preserves tombstone knowledge and keeps repair idempotent.

## 6. State-transition table (split: business vs state mutations)

Committed atomically in step 13. **Business** mutations touch files (step 11) and imply a new hash; **state-only** mutations touch only `state.json`.

| Outcome | Kind | `hashes[path]` |
|---|---|---|
| `autoUpdate` / `new` / overwrite (tmpl written) | business | set `hash(tmpl)` |
| safe-delete (orphan removed from disk) | business | remove entry |
| `unchanged` state-heal (untracked, or tombstone cleared) | state-only | set `hash(tmpl)` |
| `skip` (user kept version) | state-only | **unchanged** (stays → next run still `changed`) |
| `create-new` (tmpl parked as `.new`) | business(write `.new`) | **unchanged** for main file; `.new` never hashed |
| `userDeleted` | state-only | set `null` (tombstone) |
| `deadOrphan` | state-only | remove entry |
| `orphanedManaged` preserved | state-only | keep entry (re-reported) |

Rule: only template-content business writes set a real hash; tombstones persist until the file genuinely returns (row1); `.new` never hashed; dead orphans pruned.

## 7. Transactionality & crash recovery

- Per-file write: temp + `os.replace`.
- All `update`-mutable state in `state.json` (D12): one atomic `os.replace` (temp+fsync+rename) after all business writes + config backfill. `config.yaml` otherwise untouched by `update`.
- `.lock` (flock) prevents concurrent runs.
- `.pending` set before first write, removed after state commit. On startup `.pending` present → previous run interrupted → **abort, advise `restore from .rtmpl/.backup-<ts>/` using its manifest.json`** (no auto recovery). `rtmpl restore <backup>` and `update --resume` deferred (§14).

## 8. State health & repair

`load_state → (state, status)` ∈ {`ok`, `missing`, `corrupt`, `unsupported`, `version_unknown`}:

- `update`/`status` require `ok`. `missing` → `new`/`adopt`; `corrupt`/`unsupported`/`version_unknown` → `repair`.
- `new` creates fresh; `adopt` creates from missing (`--repair` to overwrite corrupt).
- `repair` rebuilds `state.json` from disk vs rendered template using **repair semantics** (§5: missing current-template files → tombstone). Never edits `config.yaml` or business files. Idempotent.

## 9. `changed` / `orphanedManaged` resolution

- Interactive: `[1] overwrite [2] skip [3] create-new` + all-variants; orphan safe-delete `[y] delete [n] keep` (+ all).
- `--no-input`: any unresolved → **abort before backup**. `--force` = overwrite all `changed` + safe-delete all pristine orphans. `--skip` = skip all `changed` + preserve all orphans.
- `--dry-run` = report only.
- `create-new` → collision-safe `.new` path (gitignored): if `<file>.new` already exists (a leftover merge artifact), allocate `<file>.new.1`, `.2`, … so it is never overwritten; the actual path written is reported. The user deletes the `.new` after merging.

## 10. Package layout

```
rtmpl/
├── cli.py
├── commands/{new,update,adopt,status,list,repair}.py
├── core/{state,hash,render,classify,version,tx,backup,template}.py
└── templates/batchcom-research/   # template.yaml NOT walked downstream
pyproject.toml   # [project.scripts] rtmpl="rtmpl.cli:main"; package-data templates
```
- `state.py`: `load_state→(state,status)` with path-key validation; atomic save; tombstone helpers.
- `classify.py`: 8 rows over `template_paths ∪ recorded_paths`.
- `tx.py`: lock/pending/temp+replace/interrupt detect.
- `backup.py`: snapshot disk-present universe + manifest.json.
- `template.py`: read `template.yaml`, walk payload (hard-excludes), `importlib.resources`.

## 11. Implementation Checklist

1. Scaffold `rtmpl/` + `pyproject.toml`.
2. Relocate template → `rtmpl/templates/batchcom-research/` + `template.yaml`.
3. `core/hash.py` (text/binary).
4. `core/state.py` (load+status+path-key validation, atomic save, tombstones).
5. `core/template.py` (walk + hard-excludes + importlib).
6. `core/render.py` (scoped substitution + validation + residual check).
7. `core/classify.py` (8 rows).
8. `core/version.py` (skew).
9. `core/tx.py` (lock/pending/atomic/interrupt).
10. `core/backup.py` (universe snapshot + manifest).
11. `commands/new.py`, `update.py`, `adopt.py`, `repair.py`, `status.py`, `list.py`, `cli.py`.
12. Verify + docs (§13).

## 12. Migration & cleanup

- Move `templates/batchcom-research-template/` → `rtmpl/templates/batchcom-research/`.
- Rewrite `AGENTS.md` "Set the two placeholders" line (config-driven; descriptive prose, not a render site).
- Keep `src/paths.py` `DATA_ROOT`/`DATA_CACHE` (server-disk constants).
- Add to downstream `.gitignore`: `.rtmpl/.backup-*/`, `.rtmpl/*.tmp`, `.rtmpl/.lock`, `.rtmpl/.pending`, `*.new`. (`config.yaml`, `state.json` tracked.)
- `diffusion-neural-operator`: `rtmpl adopt` once ready.

## 13. Verification

- `list` → `batchcom-research`.
- `new` → no residual tokens; `config.yaml`+`state.json` present; `template.yaml` not downstream; version only in `state.json`.
- `new` non-empty dir → error; `--force` overwrites.
- `--var proj='bad/slug'` → rejected.
- edit template → `update --dry-run` → `autoUpdate`, no backup.
- hand-edit `AGENTS.md` → `--dry-run` → `changed`.
- `update --no-input` w/ unresolved → aborts before backup.
- `update` → backup (universe) + manifest.json after confirm; lock/pending cleared; version bumped.
- **adopt-clobber**: adopt customized `AGENTS.md` → `update` → `changed` (not auto-overwrite).
- **adopt-new-file**: adopt missing template file → `update` → `new` (added, not tombstoned).
- **repair-no-recreate**: corrupt state on a project where a managed file was deleted → `repair` → tombstone → `update` does NOT recreate.
- **tombstone-return**: delete a managed file (`update`→tombstone), then restore it equal to template → `update` → `unchanged` + tombstone cleared.
- **orphan**: remove template file → `orphanedManaged`; pristine→safe-delete, modified→preserved, gone→pruned.
- **equal-version drift**: at equal version with a hand-edited file → `update` → `changed` (not no-op).
- **path-key safety**: inject `..`/absolute/`.git` key into `state.json` → `load_state` → `corrupt` → repair.
- **create-new collision**: select create-new twice for the same file → second writes `<file>.new.1`, the first artifact is preserved (no silent overwrite).
- **binary**: `*.pdf` byte-exact, raw hash, never rendered.
- **skew**: older tool vs newer project → abort w/o `--allow-downgrade`.
- **interrupt**: kill mid-write → `.pending` remains → next run aborts, points to backup+manifest.
- `uv tool install git+<repo>` → global `rtmpl`, offline `list`.

## 14. Out of Scope

- Line-level / 3-way Markdown merge (agent + `.new`).
- Full migration manifest (trellis rename/rename-dir/delete). Minimal `orphanedManaged` safe-delete only.
- Automated GitHub remote creation in `new`.
- `rich` styling.
- `rtmpl restore <backup>` and `update --resume` (interrupted runs use manual restore from backup+manifest for now).

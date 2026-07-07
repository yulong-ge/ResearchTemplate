# Plan: BatchCom Research Template Refactor

- Date: 2026-07-07
- Status: Approved (design grilled & confirmed)
- Scope: `templates/batchcom-research-template/` + one global skill edit

## 1. Background

The template was built for a generic GPU platform using **mutagen** sync, **ssh-mcp** remote control, shell-script-heavy env/path management, and a heavy **autoresearch** skill (396 lines, autonomous double-loop). The new reality:

- Target platform is **BatchCom** (Ubuntu 22.04 / CUDA 13 / A100×8, two-disk layout).
- Sync is **Git** (Gitee origin), not mutagen.
- Both the **Mac** and the **BatchCom server** run opencode natively (dual-agent), editing the same Git repo.
- The template must be **human-collaborative**, not autonomous-research-flavored.

Existing problems confirmed by codebase inspection:
- `src/` is effectively empty; the `src/<project>/paths.py` that AGENTS.md + autoresearch reference **does not exist**.
- `scripts/remote_sync.sh` still calls mutagen; `remote_targets.sh` references `REMOTE_MUTAGEN_FILE`.
- autoresearch references nonexistent skills (`ara-rigor-reviewer`, `ara-research-manager`, `ml-paper-writing`, `experiment-tracking-swanlab`).
- `.opencode/opencode.json` has a hardcoded Zotero API key (kept by user decision).

## 2. Resolved Decisions (design tree)

| # | Branch | Decision |
|---|---|---|
| D1 | Execution model | **Option B — dual native agent**. Mac and Server each run opencode natively; Git is the bridge. Situation 1: edit on Mac → SSH dispatch to Server. Situation 2: edit + run natively on Server. |
| D2 | Git origin | **Gitee** (China-friendly). Both ends clone from Gitee. Single `main` branch, "pull before edit, push after session" discipline. Artifacts gitignored. Use plain `git` (NOT `gh` — it is GitHub-only and irrelevant here). |
| D3 | Conflict avoidance | Code + research notes in Git; raw artifacts NEVER in Git (go to `RESULTS_ROOT` on research disk or W&B). |
| D4 | Context detection | `platform.system()` (`Darwin`→Mac, `Linux`→Server). opencode auto-injects `Platform` into agent context — agent knows at session start, zero config. `src/paths.py` mirrors it. **No `config.local.yaml`.** Hostname only if multiple servers later. |
| D5 | SSH tooling | **Retire ssh-mcp.** Native SSH + ControlMaster (in Mac `~/.ssh/config`, NOT in repo) + tmux. Login shell (`bash -lc` one-off, `-t`+tmux long jobs). |
| D6 | Scripts dir | **Clear all 6 scripts.** Dispatch rules + preflight checklist move into template `AGENTS.md`. |
| D7 | Path resolution | 3 layers (see §3). |
| D8 | Disk model | Two-disk split (see §4). |
| D9 | Env tooling | Mac = pure `uv`. Server = `conda` (big env: CUDA/torch) + `uv` (project venv inside conda). |
| D10 | Research skill | Replace `autoresearch` with lean `research-record` recording-hygiene guide (see §6). |

## 3. Path-Resolution Architecture (3 layers, separated)

The old `scripts/remote_env.sh` conflated "dispatch" (Mac→Server) and "resolve" (where am I, data, conda). Split them:

- **Layer 1 — `src/paths.py`**: single source of truth for all storage paths, platform-aware, imported by all code. Works on BOTH ends. No shell dependency.
- **Layer 2 — conda via login shell**: no hardcoded binary paths. Server `.bashrc`/login shell activates conda; `.condarc` points `envs_dirs` to local disk. Mac uses uv (no conda).
- **Layer 3 — Mac dispatch (thin)**: SSH connect + `cd` repo + run. Zero path logic, zero env vars (Layer 1 + 2 handle those). ControlMaster in Mac `~/.ssh/config`.

Answers the `-lic`/login-shell question: yes, with login shell the server profile puts `conda` on PATH and activates the default env, so scripts no longer hardcode `/opt/conda/bin/conda`.

## 4. Two-Disk Model (BatchCom)

| Disk | Path | Role | Holds |
|---|---|---|---|
| **科研盘 (research)** | `/home/dataset-assist-0/research` | durable, cross-machine, survives power cycles | everything canonical: code repo, dataset master, results/checkpoint archive |
| **本地盘 (local)** | `/home/dataset-local` | per-machine nvme high-perf, machine-persistent | training hot cache (staged copy) + conda envs |
| **系统盘 (system)** | `/`, `/home/batchcom` | ephemeral (lost on instance stop) | conda base `/opt/conda`, dotfiles only — do NOT store project data/envs here |

Principle: research disk = shared canonical; local disk = per-machine fast. Before long training, stage hot data research→local for speed.

`DATA_CACHE` usage rule (runtime, told to agent by human):
- Short / non-perf tasks → skip cache, read from research disk directly.
- Long / high-perf main training → stage to `DATA_CACHE` first.

## 5. `src/paths.py` (concrete, with placeholders)

```python
import platform
from pathlib import Path

_PROJ = "<proj>"        # project slug — edit after copying template
_CONDA_ENV = "<conda-env>"  # e.g. "ml" — edit per project

if platform.system() == "Linux":          # BatchCom server
    # research disk: durable, cross-machine — canonical home
    RESEARCH_ROOT = Path("/home/dataset-assist-0/research")
    REPO_ROOT     = RESEARCH_ROOT / _PROJ
    DATA_ROOT     = RESEARCH_ROOT / _PROJ / "data"      # dataset master (shared)
    RESULTS_ROOT  = RESEARCH_ROOT / _PROJ / "results"   # results/checkpoint archive

    # local disk: per-machine high-perf — cache + envs
    LOCAL_ROOT    = Path("/home/dataset-local")
    DATA_CACHE    = LOCAL_ROOT / _PROJ / "data"         # staged hot copy for training
    CONDA_ENV     = _CONDA_ENV
    # uv builds project .venv inside conda env at REPO_ROOT/.venv (gitignored)
else:                                      # Mac (darwin)
    REPO_ROOT     = Path.home() / "code" / _PROJ
    DATA_ROOT     = None       # accessing raises "run on Server"
    RESULTS_ROOT  = None
    DATA_CACHE    = None
    CONDA_ENV     = None       # Mac uses uv only, no conda
```

Two placeholders (`<proj>`, `<conda-env>`) are edited by the user after copying the template.

## 6. Research Recording (replaces `autoresearch`)

### 6.1 New skill: `research-record`

- **Role**: lean "recording-hygiene" guide (~80 lines). Tells the agent WHERE each info type goes and WHEN to update. Agent decides research rhythm (human-collaborative, NOT autonomous).
- **Carries `templates/`** with the 7 research-file skeletons so the agent can initialize a workspace by reference.

### 6.2 Cut from autoresearch

Double-loop engine, scheduler/`/loop` autonomy, pre-registration forced ordering, HTML progress-report generation, `experiments/protocols|logs|results/<hypothesis-slug>/` 4-level nesting, `ara/`, `exploration-tree.yaml`, `research/archive/`, `to_human/`, references to nonexistent skills (`ara-*`, `ml-paper-writing`, `experiment-tracking-swanlab`).

**Kept**: `ctx_memory`/`ctx_search` (OpenCode tool, NOT a research file), file-location conventions, "read overview.md first" discipline, W&B boundary, lightweight Git conventions, "negative results are progress".

### 6.3 The 7 research files (responsibilities non-overlapping)

```
research/
├── overview.md      # A+G live state — session-resume entry point (only full-read file)
├── log.md           # H append-only timeline — one-liner + link per event
├── ideas.md         # B generative — hypotheses (w/ prediction+rationale), candidate/parked/rejected
├── findings.md      # E+F synthesis — mature conclusions, cross-run patterns, constraints, open scientific Qs
├── decisions.md     # G-decisions — decision + rationale + alternatives (topic-retrievable, not chronological)
├── environment.md   # I provenance — conda env, CUDA/GPU, pkg versions, data/model registry, seeds (human-readable)
├── runs/            # C+D one record per significant experiment (ELN heart)
│   └── <YYYY-MM-DD>-<slug>.md
├── literature/      # reading notes
│   └── survey.md
└── paper/           # manuscript (empty placeholder)
```

### 6.4 Three disciplines (enforced in skill + AGENTS.md)

1. **`runs/` admission threshold**: throwaway/exploration runs → `log.md` one-liner only; significant runs (test a hypothesis / citable result / surprise) → `runs/<slug>.md`. Exploratory runs that turn significant get promoted (write `runs/` entry, update `log.md` line to link).
2. **Pointer pattern (no content duplication)**: each fact has exactly ONE home; other files hold LINKS not copies. `log.md` and `overview.md` are indexes (summary + link), never re-narrate full content. `runs/` records are immutable historical snapshots.
3. **Typed read strategy**: `overview.md` = curated small (~150 lines), the ONLY blind full-read; append-only files (`log.md`) read by tail; cumulative files (`findings.md`, `ideas.md`, `decisions.md`, `environment.md`) read by grep/offset, never blind full-read, archive when >~300 lines; per-record files (`runs/<slug>.md`) read individually by link/grep.

### 6.5 `runs/<slug>.md` template (scientific method mirror)

```
# <date> <slug>

## Status
CONFIRMATORY | EXPLORATORY  ；  POSITIVE | NEGATIVE | INCONCLUSIVE

## Hypothesis & Prediction (write BEFORE running)
- Hypothesis (H#): ...   (see ideas.md#H#)
- Prediction: ...
- Rationale (why expected): ...

## Method
- What changed: ...
- Config/hyperparams: → W&B run <link>
- Code: git <commit> @ <branch>
- Command: ...
- Data: <dataset/version> @ <path>

## Results
- Key metric(s): ...  (full curves/media → W&B)
- Observations/anomalies: ...
- Sanity check: converged? baseline reproduced? ✓/✗

## Interpretation
- What it means: ...
- Confirms/rejects hypothesis?

## Follow-ups
- Suggests: ... (sync to ideas.md / findings.md with links)
```

### 6.6 W&B vs Markdown boundary

- **→ W&B**: metrics, curves, media, hyperparams, system metrics, config snapshot, code version, data/model artifacts (versioned). NEVER checkpoints/`.pt`/`.safetensors`/caches.
- **→ Markdown**: human narrative, interpretation, decision rationale, single-run "what it means", mature conclusions, ideas, human-readable provenance.
- **→ gitignored (neither)**: large raw artifacts (checkpoints, latent caches) — `paths.py` points to `RESULTS_ROOT` on research disk.

## 7. Template `AGENTS.md` Rewrite Scope

Sections to write:
- **Two-disk model** (§4) + `paths.py` as single source of truth.
- **Dispatch rules** (Mac→Server, situation 1 only):
  - one-off: `ssh batchcom-a100 'bash -lc "cd <repo> && conda activate <env> && uv run python ..."'`
  - long: `ssh -t batchcom-a100 'tmux new -s <name> "cd <repo> && conda activate <env> && uv run python -m train"'`
  - preflight checklist (run before remote GPU work): nvidia-smi, df, torch.cuda check — as a documented command list, NOT a script.
- **Env tooling split**: Mac = uv only; Server = conda(big) + uv(venv).
- **Research file set** (§6.3) + read discipline (§6.4).
- **W&B boundary** (§6.6).

Sections to remove:
- All `ara-*` / `ml-paper-writing` / `experiment-tracking-swanlab` references.
- `experiments/` multi-level nesting description.
- `ara/`, `ctx_memory`-as-research-file, `exploration-tree.yaml` references (ctx_memory stays as a tool).
- mutagen references.

## 8. Implementation Checklist

| # | Action | Detail |
|---|---|---|
| 1 | Create `src/paths.py` | Per §5, BatchCom real paths, two placeholders. |
| 2 | Delete `scripts/` contents | Remove all 6 shell scripts (`remote_targets.sh`, `remote_env.sh`, `remote_python.sh`, `remote_run.sh`, `remote_sync.sh`, `remote_preflight.sh`) + stale `src/__pycache__/project_paths.cpython-312.pyc`. Decide dir keep-as-empty vs remove. |
| 3 | Delete `autoresearch` skill; create `research-record` skill | Per §6.1–6.2. Skill includes `templates/` with 7-file skeletons (§6.3) + runs template (§6.5). |
| 4 | Rewrite template `AGENTS.md` | Per §7. |
| 5 | Create `research/` file templates | overview/log/ideas/findings/decisions/environment + `runs/` + `literature/survey.md` + `paper/` placeholder. |
| 6 | Edit `.opencode/agents/remote-exec.md` | Drop `ssh-mcp_*` permission; switch to bash+SSH+tmux channel; keep name + read-only role. |
| 7 | Edit `.opencode/opencode.json` | Set `ssh-mcp.enabled = false`. **Leave Zotero key untouched** (user decision). |
| 8 | Edit global `~/.agents/skills/remote-terminal-tool-strategy/SKILL.md` | Remove ssh-mcp section ONLY; do NOT alter any other wording/logic (user-crafted distinctions). |
| 9 | Update `.gitignore` | Add `.venv/`, `wandb/`, large results/checkpoints, conda envs, local secrets. Keep `research/*.md` tracked. |
| 10 | BatchCom `.condarc` | Set `envs_dirs: [/home/dataset-local/conda/envs]` so new conda envs land on persistent local disk (not ephemeral system disk). |

## 9. Out of Scope

- No framework runtime / scheduler / manifest / file-sync daemon (per root AGENTS.md).
- No multi-server support yet (single BatchCom target; revisit hostname-keyed paths if needed).
- No automated ctx_memory population.
- Zotero key security hardening (explicitly deferred by user).

## 10. Verification After Implementation

- `bash -n` on any remaining shell (likely none).
- `python -c "from src.paths import *"` on both Mac and Server (Mac: paths resolve to None gracefully; Server: resolves to BatchCom paths).
- Confirm `research-record` skill loads and `templates/` are complete.
- Confirm `ssh-mcp` disabled; `remote-exec` agent still dispatches via raw SSH.
- Grep template for residual `mutagen`, `ara-`, `ml-paper-writing`, `REMOTE_MUTAGEN_FILE`, `ssh-mcp` references → expect zero.

# BatchCom Research Workspace

## Resume
- Read `research/overview.md` first (the only file meant for full-read; keep <~150 lines).
- For anything you record, use the `research-record` skill — it owns the where-each-fact-lives table, read discipline, and W&B boundary. Scaffold a fresh workspace from its `templates/`.

## Context
opencode injects `Platform` (`darwin` = Mac, `linux` = BatchCom server); `src/paths.py` mirrors it. You always know which end you're on.
- **Mac:** edit, lint, small CPU tests only. No GPU; `DATA_ROOT`/`RESULTS_ROOT` resolve to `None` and raise on access.
- **Server:** full execution.

## Paths
`src/paths.py` is the single source of truth — import it, never hardcode. Set the two placeholders per project: `<proj>`, `<conda-env>`.

Server disk policy (the part `paths.py` does not explain):
| Disk | Path | Policy |
|---|---|---|
| Research | `/home/dataset-assist-0/research` | durable, cross-machine — repo, dataset master, results |
| Local | `/home/dataset-local` | per-machine fast — training hot cache + conda envs |
| System | `/`, `/home/batchcom` | ephemeral (lost on instance stop) — never put project data or envs here |

## Environment
- **Mac:** `uv` only (`uv venv`, `uv run`).
- **Server:** `conda` for the big env (CUDA/torch — what uv cannot install); `uv` builds the project `.venv` (gitignored) inside it.
- Route new conda envs to local disk (one-time per server) — `~/.condarc`:
  ```yaml
  envs_dirs: [/home/dataset-local/conda/envs]
  pkgs_dirs: [/home/dataset-local/conda/pkgs]
  ```

## Running code
- **Server:** run directly in a tmux session — `conda activate <env> && uv run python ...`.
- **From Mac:** native SSH + ControlMaster (in the Mac's `~/.ssh/config`, not in this repo) + tmux. The login shell resolves `conda` — never hardcode a conda binary.
  - One-off: `ssh batchcom-a100 'bash -lc "cd <repo> && conda activate <env> && uv run python ..."'`
  - Long job: `ssh -t batchcom-a100 'tmux new -s <name> "cd <repo> && conda activate <env> && uv run python -m train"'`
  - Preflight before GPU work: `ssh batchcom-a100 'bash -lc "nvidia-smi; df -h /home/dataset-local /home/dataset-assist-0/research; python -c \"import torch;print(torch.cuda.is_available())\""'`
- `DATA_CACHE`: stage hot data research→local only for long / high-perf training; short tasks read straight from the research disk.

## Git
- Origin is **Gitee**. Use plain `git` (not `gh` — GitHub-only, irrelevant here).
- Single `main`: `git pull --rebase` before editing, `git push` at session end.
- Never commit raw artifacts (checkpoints, caches, large outputs) → `RESULTS_ROOT` (gitignored) or W&B. Full boundary in `research-record`.

## Verify
- `uv run python -c "from src.paths import REPO_ROOT; print(REPO_ROOT)"`
- `uv run pytest tests/`
- Residual sweep (expect zero hits): `rg -n 'mutagen|ara-rigor|ara-research|ssh-mcp|REMOTE_MUTAGEN' .`

## Conventions
- Replacing an obsolete design: remove the old path directly; no compatibility shims, legacy aliases, or migration wrappers.
- conda never `base`; check `nvidia-smi` and `df -h` before large training or downloads; don't swallow critical model/data/config failures.
- Don't start `/loop`, cron, or watchdog jobs unless the user explicitly asks for continuous autonomous operation.

## Skills
- `research-record` — any recording or resume.
- `idea-evaluator` — evaluate a candidate idea (run in a fresh subagent).
- `weights-and-biases` — experiment tracking (prefer over tensorboard).
- `grill-me` — stress-test a plan before implementing.

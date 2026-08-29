# BatchCom Research Workspace

## Resume
- Read `research/overview.md` first (the only file meant for full-read; keep <~150 lines).
- For recording or reconciliation, use the global `research-record` skill. This repository's README and instructions own the concrete file layout; the global skill does not.

## Research records
- Keep cross-experiment state under `research/`; keep experiment protocol, committed config, and milestone analysis under `experiments/<id>/`.
- Do not create per-run Markdown or custom run JSON by default. The selected experiment tracker and durable results store own run-level state; `analysis.md` records only conclusions worth retaining and links to runs.
- Operational heartbeats and routine health checks stay in machine logs or tracker state. Update Markdown only at launch, protocol change, failure/recovery that changes interpretation, a coarse checkpoint/result milestone, or completion.
- A project may replace this default only through an explicit project-level policy or skill. Existing code, tracker layouts, or conventions from another repository do not change it.
- Reconciliation may correct current-state documentation from verified evidence, but must preserve historical results and must not silently change governance or methodology.

## Context
opencode injects `Platform` (`darwin` = Mac, `linux` = BatchCom server); `src/paths.py` mirrors it. You always know which end you're on.
- **Mac:** edit, lint, small CPU tests only. No GPU; canonical asset and server-cache roots resolve to `None` and raise on access.
- **Server:** full execution.

## Paths
`src/paths.py` is the single source of truth — import it, never hardcode. Project values (`<proj>`, `<conda-env>`) are rendered from `.rtmpl/config.yaml` by `rtmpl` at scaffold/update time; edit them there, not in source.

- **Research NFS (canonical):** shared assets → `SHARED_DATA_ROOT` / `SHARED_MODEL_ROOT`; project assets → `DATA_ROOT` / `MODEL_ROOT` / `RESULTS_ROOT`.
- **Local NVMe (performance):** staged project data → `DATA_CACHE`; shared HF/Torch/uv downloads → `LIB_CACHE`. Neither is the canonical copy.
- **System disk:** do not store research data, models, results, caches, or environments under `/`, `/home/batchcom`, or `/tmp`.
- Run-directory naming and layout below `RESULTS_ROOT` belong to the project or its training/tracking framework; this template does not define a `run_id` scheme.
- Code under `external/` follows its upstream path contract, including required relative data/output paths. Do not relocate those paths unless explicitly integrating that code into the project-owned layout.

## Environment
- **Mac:** `uv` only (`uv venv`, `uv run`).
- **Server:** `conda` for the big env (CUDA/torch — what uv cannot install); `uv` builds the project `.venv` (gitignored) inside it. Conda envs live on the local disk (`/home/dataset-local/conda/envs`, per the server `.condarc`).

## Running code
- **Server:** run directly in a tmux session — `conda activate <env> && uv run python ...`.
- **From Mac:** native SSH + ControlMaster (in the Mac's `~/.ssh/config`, not in this repo) + tmux. The login shell resolves `conda` — never hardcode a conda binary.
  - One-off: `ssh batchcom-a100 'bash -lc "cd <repo> && conda activate <env> && uv run python ..."'`
  - Long job: `ssh -t batchcom-a100 'tmux new -s <name> "cd <repo> && conda activate <env> && uv run python -m train"'`
  - Preflight before GPU work: `ssh batchcom-a100 'bash -lc "nvidia-smi; df -h /home/dataset-local /home/dataset-assist-0/research; python -c \"import torch;print(torch.cuda.is_available())\""'`
- Stage project data to `DATA_CACHE` only when NFS I/O is the bottleneck; otherwise read `DATA_ROOT` directly.

## Git
- Origin is **Gitee**. Use plain `git` (not `gh` — GitHub-only, irrelevant here).
- Single `main`: `git pull --rebase` before editing, `git push` at session end.
- Never commit raw artifacts. Durable outputs go below `RESULTS_ROOT` (gitignored); metrics/curves/media also go to W&B when configured. Full boundary in `research-record`.

## Verify
- `uv run python -c "from src.paths import REPO_ROOT, RESULTS_ROOT; print(REPO_ROOT, RESULTS_ROOT)"`
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

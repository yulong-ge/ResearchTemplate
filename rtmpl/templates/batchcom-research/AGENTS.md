# BatchCom Research Workspace

## Human-owned workflow

- A human creates one Plan in `docs/plans/` for each requested experiment or engineering task.
- The Plan supplies the question, relevant context, allowed reads, writable paths, commands,
  resources, budget, and stop conditions.
- Before acting, the Agent returns a concrete execution plan, file list, commands, expected
  outputs, and risks, then waits for explicit approval.
- The Plan names the context the Agent may read and the paths it may edit. The Agent works within
  that scope and waits for a new Plan when the task needs additional context.
- The Agent reports raw outputs, errors, and observations. A human organizes notes, interprets
  results, and decides what belongs in later Plans or papers.

## Directory ownership

| Path | Owner | Contract |
|---|---|---|
| `docs/plans/` | Human | Task entry points and execution authorization |
| `notes/` | Human | Background, environment, provenance, and research notes |
| `experiments/` | Human | Results, logs, configurations, and raw artifacts |
| `literature/` | Human | Paper notes and references |
| `paper/` | Human | Manuscript material |
| `.rtmpl/` | `rtmpl` | Template lifecycle metadata only |

Choose an `experiments/` directory name that makes sense for the current task and put the outputs
requested by the Plan there. The Plan may define a filename convention or result format when the
task benefits from one.

## Paths and storage

`src/paths.py` is the single source of truth. Project values are rendered from
`.rtmpl/config.yaml`; do not hardcode server paths in scripts.

- Research NFS: `SHARED_DATA_ROOT`, `SHARED_MODEL_ROOT`, `DATA_ROOT`, `MODEL_ROOT`, and
  `RESULTS_ROOT` are canonical.
- Local NVMe: `DATA_CACHE` and `LIB_CACHE` are disposable acceleration layers; keep canonical
  copies under the declared research roots.
- System disk, `/home/batchcom`, and `/tmp` must not hold research assets, models, results,
  caches, or environments.

## Environment and execution

- Mac uses `uv` for environments and CPU checks. No GPU work runs locally.
- BatchCom uses conda for CUDA/torch and `uv` for the project environment. Conda environments
  live under `/home/dataset-local/conda/envs`.
- On BatchCom, run in tmux: `conda activate <env> && uv run python ...`.
- From Mac, use native SSH and tmux. Preflight GPU work with `nvidia-smi`, disk checks, and a
  torch CUDA check before starting a GPU task.

## Git and verification

Keep raw artifacts out of Git. Run the project's tests and the relevant command checks after
changes. `rtmpl status` reports template differences; it does not report research progress.

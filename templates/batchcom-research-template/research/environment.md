# Environment & Provenance

<!--
  Human-readable provenance for reproducibility. The actual path strings are
  resolved by src/paths.py; this file records the DESCRIPTION + versions +
  registry a human needs.

  Update when the environment, key datasets, or canonical checkpoints change.
-->

## Storage Layout (BatchCom server)

Two-disk model — see `src/paths.py` (single source of truth) and the server's
`~/.bashrc_custom` for the cache env-var exports.

| Disk | Path | Role | Holds |
|---|---|---|---|
| Research (durable) | `/home/dataset-assist-0/research` | cross-machine, survives restarts | repo, dataset master (`DATA_ROOT`), results archive (`RESULTS_ROOT`) |
| Local (nvme, fast) | `/home/dataset-local` | per-machine high-perf | `DATA_CACHE` (project hot data), `LIB_CACHE` (HF/torch downloads), conda envs |
| System (ephemeral) | `/`, `~` | lost on instance stop | **never** put project data, caches, or envs here |

Library caches (`HF_HOME`, `HF_HUB_CACHE`, `TRANSFORMERS_CACHE`, `HF_DATASETS_CACHE`,
`TORCH_HOME`) are exported in the server's `~/.bashrc_custom` to
`/home/dataset-local/cache`, so HF/torch downloads never fill `~`. `DATA_CACHE`
and `LIB_CACHE` are distinct: the former is project-scoped staged training data,
the latter is a cross-project shared library download cache.

## Compute

- **Platform:** <!-- BatchCom A100×8 / Mac -->
- **CUDA:** <!-- e.g. 13.0 -->
- **GPU(s):** <!-- e.g. NVIDIA A100-SXM4-80GB × 8 -->
- **Conda env (server):** <!-- name from src/paths.py CONDA_ENV -->
- **Python:** <!-- e.g. 3.12 -->

## Key Packages

<!-- torch, transformers, ... with versions. Pin in pyproject.toml / uv.lock. -->

## Data Registry

| Dataset | Version / split | Location | Notes |
|---|---|---|---|
| | | `DATA_ROOT/...` | |

## Model / Checkpoint Registry

| Checkpoint | Producing run | Location | Purpose |
|---|---|---|---|
| | `runs/<slug>.md` | `RESULTS_ROOT/...` | |

## Seeds & Reproducibility Notes

<!-- random seeds used, determinism caveats, non-deterministic ops -->

# Environment & Provenance

<!--
  Human-readable provenance for reproducibility. The actual path strings are
  resolved by src/paths.py; this file records the DESCRIPTION + versions +
  registry a human needs.

  Update when the environment, key datasets, or canonical checkpoints change.
-->

## Storage Layout (BatchCom server)

See `src/paths.py` for resolved paths and `~/.bashrc_custom` for library-cache
environment variables.

| Storage | Path | Durability contract | Holds |
|---|---|---|---|
| Research NFS | `/home/dataset-assist-0/research` | canonical, cross-machine, restart-independent | repo, shared/project data and models, results |
| Local NVMe | `/home/dataset-local` | performance storage; not the canonical root | staged project data, library caches, conda envs |
| System/container | `/`, `~`, `/tmp` | ephemeral and small | **never** store research assets here |

Shared assets use `SHARED_DATA_ROOT` / `SHARED_MODEL_ROOT`; project assets use
`DATA_ROOT` / `MODEL_ROOT` / `RESULTS_ROOT`. `DATA_CACHE` and `LIB_CACHE` are
performance caches, not canonical asset locations. Run IDs and subdirectories
below `RESULTS_ROOT` are managed by the project, Lightning, W&B, or another
selected framework.

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
| | | `DATA_ROOT/...` or `SHARED_DATA_ROOT/...` | |

## Model / Checkpoint Registry

| Model / checkpoint | Version / producing run | Location | Purpose |
|---|---|---|---|
| | | `MODEL_ROOT/...`, `SHARED_MODEL_ROOT/...`, or `RESULTS_ROOT/...` | |

## Seeds & Reproducibility Notes

<!-- random seeds used, determinism caveats, non-deterministic ops -->

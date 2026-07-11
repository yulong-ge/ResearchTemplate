# Environment & Provenance

<!--
  Human-readable provenance for reproducibility. The actual path strings are
  resolved by src/paths.py; this file records the DESCRIPTION + versions +
  registry a human needs.

  Update when the environment, key datasets, or canonical checkpoints change.
-->

## Storage Layout

- **Canonical shared:** `SHARED_DATA_ROOT`, `SHARED_MODEL_ROOT`
- **Canonical project:** `DATA_ROOT`, `MODEL_ROOT`, `RESULTS_ROOT`
- **Performance caches:** `DATA_CACHE`, `LIB_CACHE`

Caches are not canonical asset locations.

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

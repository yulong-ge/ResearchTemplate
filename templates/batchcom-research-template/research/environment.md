# Environment & Provenance

<!--
  Human-readable provenance for reproducibility. The actual path strings are
  resolved by src/paths.py; this file records the DESCRIPTION + versions +
  registry a human needs.

  Update when the environment, key datasets, or canonical checkpoints change.
-->

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

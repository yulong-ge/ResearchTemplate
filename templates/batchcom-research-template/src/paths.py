"""Project path resolution — single source of truth for storage paths.

Platform-aware: resolves to BatchCom server paths on Linux, to local Mac paths
on Darwin. Edit ``_PROJ`` and ``_CONDA_ENV`` after copying the template.

Two-disk model (BatchCom server):
  - Research disk (``/home/dataset-assist-0/research``): durable, cross-machine,
    survives power cycles. Holds every canonical asset: the repo, dataset
    master copies, and the results/checkpoint archive.
  - Local disk (``/home/dataset-local``): per-machine nvme high-perf. Holds the
    training hot cache (staged copies) and conda environments.

The system disk (``/``, ``/home/batchcom``) is ephemeral — never store project
data or conda envs there.

See ``docs/plans/2026-07-07-template-refactor.md`` for the full design.
"""
from __future__ import annotations

import platform
from pathlib import Path

# --- Edit these after copying the template ---------------------------------
_PROJ = "<proj>"  # project slug, e.g. "my-research"
_CONDA_ENV = "<conda-env>"  # server conda env name, e.g. "ml"
# ---------------------------------------------------------------------------

_IS_SERVER = platform.system() == "Linux"


def _unavailable(name: str) -> None:
    raise RuntimeError(
        f"{name} is not available on Mac (darwin). "
        "Datasets and results live on the BatchCom server — run there."
    )


if _IS_SERVER:
    # Research disk: durable, cross-machine — canonical home for everything.
    RESEARCH_ROOT: Path | None = Path("/home/dataset-assist-0/research")
    REPO_ROOT: Path = RESEARCH_ROOT / _PROJ
    DATA_ROOT: Path | None = RESEARCH_ROOT / _PROJ / "data"
    RESULTS_ROOT: Path | None = RESEARCH_ROOT / _PROJ / "results"

    # Local disk: per-machine high-perf — training hot cache + conda envs.
    LOCAL_ROOT: Path | None = Path("/home/dataset-local")
    DATA_CACHE: Path | None = LOCAL_ROOT / _PROJ / "data"
    CONDA_ENV: str | None = _CONDA_ENV
    # uv builds the project venv inside the active conda env at REPO_ROOT/.venv
    # (gitignored). Route new conda envs to the local disk via .condarc
    # ``envs_dirs`` — see research/environment.md.
else:
    # Mac (darwin): edit here, run on the server.
    REPO_ROOT: Path = Path.home() / "code" / _PROJ
    RESEARCH_ROOT = None
    LOCAL_ROOT = None
    DATA_ROOT = None
    DATA_CACHE = None
    RESULTS_ROOT = None
    CONDA_ENV = None  # Mac uses uv only; no conda.


def require_data_root() -> Path:
    """Return ``DATA_ROOT``, raising a clear error off-server."""
    if DATA_ROOT is None:
        _unavailable("DATA_ROOT")
    return DATA_ROOT


def require_results_root() -> Path:
    """Return ``RESULTS_ROOT``, raising a clear error off-server."""
    if RESULTS_ROOT is None:
        _unavailable("RESULTS_ROOT")
    return RESULTS_ROOT

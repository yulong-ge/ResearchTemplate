"""Project path resolution — single source of truth for storage paths.

Platform-aware: resolves to BatchCom server paths on Linux, to local Mac paths
on Darwin. Project values are rendered by ``rtmpl``.

Two-disk model (BatchCom server):
  - Research disk (``/home/dataset-assist-0/research``): durable NFS. Holds every
    canonical asset: repos, datasets, reusable models, and run outputs.
  - Local disk (``/home/dataset-local``): per-machine high-performance NVMe.
    Holds staged dataset copies, download caches, and conda environments.
    BatchCom persistence is optional, so it is never the canonical asset root.

The system disk (``/``, ``/home/batchcom``) is ephemeral — never store project
data, library caches, or conda envs there.

See ``research/environment.md`` for the full contract.
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
        "Research assets live on the BatchCom server — run there."
    )


if _IS_SERVER:
    # Research NFS: canonical assets. Never use a cache as the only copy.
    RESEARCH_ROOT: Path | None = Path("/home/dataset-assist-0/research")
    SHARED_DATA_ROOT: Path | None = RESEARCH_ROOT / "_shared" / "data"
    SHARED_MODEL_ROOT: Path | None = RESEARCH_ROOT / "_shared" / "models"

    REPO_ROOT: Path = RESEARCH_ROOT / _PROJ
    DATA_ROOT: Path | None = REPO_ROOT / "data"
    MODEL_ROOT: Path | None = REPO_ROOT / "models"
    RESULTS_ROOT: Path | None = REPO_ROOT / "results"

    # Local NVMe: high-performance data staging + shared library caches.
    LOCAL_ROOT: Path | None = Path("/home/dataset-local")
    DATA_CACHE: Path | None = LOCAL_ROOT / _PROJ / "data"
    LIB_CACHE: Path | None = LOCAL_ROOT / "cache"  # cross-project HF/torch downloads
    CONDA_ENV: str | None = _CONDA_ENV
    # uv builds the project venv inside the active conda env at REPO_ROOT/.venv
    # (gitignored). Route new conda envs to the local disk via .condarc
    # ``envs_dirs`` — see research/environment.md. Library cache dirs (HF_HOME,
    # TORCH_HOME, ...) are exported in the server's ~/.bashrc_custom to LIB_CACHE.
else:
    # Mac (darwin): edit here, run on the server.
    REPO_ROOT: Path = Path.home() / "code" / _PROJ
    RESEARCH_ROOT = None
    SHARED_DATA_ROOT = None
    SHARED_MODEL_ROOT = None
    LOCAL_ROOT = None
    DATA_ROOT = None
    MODEL_ROOT = None
    DATA_CACHE = None
    LIB_CACHE = None
    RESULTS_ROOT = None
    CONDA_ENV = None  # Mac uses uv only; no conda.


def _require_path(name: str, value: Path | None) -> Path:
    if value is None:
        _unavailable(name)
    return value


def require_shared_data_root() -> Path:
    """Return the canonical cross-project dataset root."""
    return _require_path("SHARED_DATA_ROOT", SHARED_DATA_ROOT)


def require_shared_model_root() -> Path:
    """Return the canonical cross-project reusable-model root."""
    return _require_path("SHARED_MODEL_ROOT", SHARED_MODEL_ROOT)


def require_data_root() -> Path:
    """Return ``DATA_ROOT``, raising a clear error off-server."""
    return _require_path("DATA_ROOT", DATA_ROOT)


def require_model_root() -> Path:
    """Return the canonical project-owned reusable-model root."""
    return _require_path("MODEL_ROOT", MODEL_ROOT)


def require_results_root() -> Path:
    """Return ``RESULTS_ROOT``, raising a clear error off-server."""
    return _require_path("RESULTS_ROOT", RESULTS_ROOT)

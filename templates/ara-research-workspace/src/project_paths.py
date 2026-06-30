from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    project_root: Path
    data_dir: Path
    models_dir: Path
    runs_dir: Path
    logs_dir: Path


def _required_env(name: str) -> Path:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} is required; run the command through rk run")
    return Path(value)


def project_paths() -> ProjectPaths:
    return ProjectPaths(
        project_root=_required_env("RK_PROJECT_ROOT"),
        data_dir=_required_env("RK_DATA_DIR"),
        models_dir=_required_env("RK_MODELS_DIR"),
        runs_dir=_required_env("RK_RUNS_DIR"),
        logs_dir=_required_env("RK_LOGS_DIR"),
    )

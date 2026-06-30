from __future__ import annotations

from pathlib import Path
import re

from rk.config import ProjectConfig


_RUN_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


def _as_posix(path: Path) -> str:
    return path.as_posix()


def _validate_run_id(run_id: str) -> str:
    if not _RUN_ID_RE.fullmatch(run_id):
        raise ValueError(f"unsafe run_id: {run_id!r}")
    return run_id


def build_run_environment(config: ProjectConfig, run_id: str, *, scratch: bool) -> dict[str, str]:
    safe_run_id = _validate_run_id(run_id)
    active_runs_dir = config.scratch_root / "runs" if scratch else config.runs_dir
    active_logs_dir = config.scratch_root / "logs" if scratch else config.logs_dir
    active_run_dir = active_runs_dir / safe_run_id
    active_log_dir = active_logs_dir / safe_run_id
    scratch_run_dir = config.scratch_root / "runs" / safe_run_id
    scratch_log_dir = config.scratch_root / "logs" / safe_run_id
    wandb_dir = active_run_dir / "wandb"

    return {
        "RK_ACTIVE_RUN": "1",
        "RK_RUN_ID": safe_run_id,
        "RK_PROJECT_ROOT": _as_posix(config.canonical_root),
        "RK_CANONICAL_PROJECT_ROOT": _as_posix(config.canonical_root),
        "RK_SCRATCH_ROOT": _as_posix(config.scratch_root),
        "RK_DATA_DIR": _as_posix(config.data_dir),
        "RK_MODELS_DIR": _as_posix(config.models_dir),
        "RK_RUNS_DIR": _as_posix(active_runs_dir),
        "RK_LOGS_DIR": _as_posix(active_logs_dir),
        "RK_CANONICAL_RUNS_DIR": _as_posix(config.runs_dir),
        "RK_CANONICAL_LOGS_DIR": _as_posix(config.logs_dir),
        "RK_RUN_DIR": _as_posix(active_run_dir),
        "RK_LOG_DIR": _as_posix(active_log_dir),
        "RK_SCRATCH": "1" if scratch else "0",
        "RK_SCRATCH_RUN_DIR": _as_posix(scratch_run_dir),
        "RK_SCRATCH_LOG_DIR": _as_posix(scratch_log_dir),
        "WANDB_DIR": _as_posix(wandb_dir),
        "WANDB_ARTIFACT_DIR": _as_posix(wandb_dir / "artifacts"),
        "WANDB_CACHE_DIR": _as_posix(wandb_dir / "cache"),
        "WANDB_CONFIG_DIR": _as_posix(wandb_dir / "config"),
        "WANDB_DATA_DIR": _as_posix(wandb_dir / "data"),
    }

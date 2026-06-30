from pathlib import Path

import pytest

from rk.config import ProjectConfig
from rk.env import build_run_environment


def make_config() -> ProjectConfig:
    return ProjectConfig(
        name="demo",
        target="batchcom",
        canonical_root=Path("/home/dataset-assist-0/research/demo"),
        scratch_root=Path("/home/dataset-local/demo"),
        data_dir=Path("/home/dataset-assist-0/research/demo/data"),
        models_dir=Path("/home/dataset-assist-0/research/demo/models"),
        runs_dir=Path("/home/dataset-assist-0/research/demo/runs"),
        logs_dir=Path("/home/dataset-assist-0/research/demo/logs"),
    )


def test_canonical_run_environment():
    env = build_run_environment(make_config(), run_id="rk-20260630-abc123", scratch=False)

    assert env["RK_PROJECT_ROOT"] == "/home/dataset-assist-0/research/demo"
    assert env["RK_CANONICAL_PROJECT_ROOT"] == "/home/dataset-assist-0/research/demo"
    assert env["RK_DATA_DIR"] == "/home/dataset-assist-0/research/demo/data"
    assert env["RK_MODELS_DIR"] == "/home/dataset-assist-0/research/demo/models"
    assert env["RK_RUNS_DIR"] == "/home/dataset-assist-0/research/demo/runs"
    assert env["RK_LOGS_DIR"] == "/home/dataset-assist-0/research/demo/logs"
    assert env["RK_CANONICAL_RUNS_DIR"] == "/home/dataset-assist-0/research/demo/runs"
    assert env["RK_CANONICAL_LOGS_DIR"] == "/home/dataset-assist-0/research/demo/logs"
    assert env["RK_RUN_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123"
    assert env["RK_LOG_DIR"] == "/home/dataset-assist-0/research/demo/logs/rk-20260630-abc123"
    assert env["RK_RUN_ID"] == "rk-20260630-abc123"
    assert env["RK_ACTIVE_RUN"] == "1"
    assert env["RK_SCRATCH"] == "0"
    assert env["WANDB_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123/wandb"
    assert env["WANDB_ARTIFACT_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123/wandb/artifacts"
    assert env["WANDB_CACHE_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123/wandb/cache"
    assert env["WANDB_CONFIG_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123/wandb/config"
    assert env["WANDB_DATA_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123/wandb/data"
    assert "WANDB_RUN_ID" not in env


def test_scratch_run_environment():
    env = build_run_environment(make_config(), run_id="rk-20260630-abc123", scratch=True)

    assert env["RK_SCRATCH"] == "1"
    assert env["RK_RUNS_DIR"] == "/home/dataset-local/demo/runs"
    assert env["RK_LOGS_DIR"] == "/home/dataset-local/demo/logs"
    assert env["RK_RUN_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123"
    assert env["RK_LOG_DIR"] == "/home/dataset-local/demo/logs/rk-20260630-abc123"
    assert env["RK_SCRATCH_RUN_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123"
    assert env["WANDB_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123/wandb"
    assert env["WANDB_ARTIFACT_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123/wandb/artifacts"
    assert env["WANDB_CACHE_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123/wandb/cache"
    assert env["WANDB_CONFIG_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123/wandb/config"
    assert env["WANDB_DATA_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123/wandb/data"


@pytest.mark.parametrize("run_id", ["", ".", "..", "../escape", "/tmp/escape", "nested/run"])
def test_run_environment_rejects_unsafe_run_id(run_id: str):
    with pytest.raises(ValueError, match="unsafe run_id"):
        build_run_environment(make_config(), run_id=run_id, scratch=False)

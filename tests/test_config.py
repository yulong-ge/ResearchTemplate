from pathlib import Path

import pytest

from rk.config import ProjectConfig, load_project_config


def test_load_project_config(tmp_path: Path):
    config_dir = tmp_path / ".rk"
    config_dir.mkdir()
    (config_dir / "project.toml").write_text(
        """
[project]
name = "demo"
target = "batchcom"

[paths]
canonical_root = "/home/dataset-assist-0/research/demo"
scratch_root = "/home/dataset-local/demo"
data_dir = "/home/dataset-assist-0/research/demo/data"
models_dir = "/home/dataset-assist-0/research/demo/models"
runs_dir = "/home/dataset-assist-0/research/demo/runs"
logs_dir = "/home/dataset-assist-0/research/demo/logs"
""".strip(),
        encoding="utf-8",
    )

    config = load_project_config(tmp_path)

    assert config == ProjectConfig(
        name="demo",
        target="batchcom",
        canonical_root=Path("/home/dataset-assist-0/research/demo"),
        scratch_root=Path("/home/dataset-local/demo"),
        data_dir=Path("/home/dataset-assist-0/research/demo/data"),
        models_dir=Path("/home/dataset-assist-0/research/demo/models"),
        runs_dir=Path("/home/dataset-assist-0/research/demo/runs"),
        logs_dir=Path("/home/dataset-assist-0/research/demo/logs"),
        guard_mode="strict",
    )


def test_missing_project_config_fails(tmp_path: Path):
    with pytest.raises(FileNotFoundError, match=".rk/project.toml"):
        load_project_config(tmp_path)


def test_placeholder_project_config_fails(tmp_path: Path):
    config_dir = tmp_path / ".rk"
    config_dir.mkdir()
    (config_dir / "project.toml").write_text(
        """
[project]
name = "CHANGE_ME"
target = "batchcom"

[paths]
canonical_root = "/home/dataset-assist-0/research/CHANGE_ME"
scratch_root = "/home/dataset-local/CHANGE_ME"
data_dir = "/home/dataset-assist-0/research/CHANGE_ME/data"
models_dir = "/home/dataset-assist-0/research/CHANGE_ME/models"
runs_dir = "/home/dataset-assist-0/research/CHANGE_ME/runs"
logs_dir = "/home/dataset-assist-0/research/CHANGE_ME/logs"
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="replace CHANGE_ME"):
        load_project_config(tmp_path)

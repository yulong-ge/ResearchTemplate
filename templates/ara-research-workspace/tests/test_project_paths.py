import os

import pytest

from src.project_paths import project_paths


def test_project_paths_from_rk_environment(monkeypatch):
    monkeypatch.setenv("RK_PROJECT_ROOT", "/research/demo")
    monkeypatch.setenv("RK_DATA_DIR", "/research/demo/data")
    monkeypatch.setenv("RK_MODELS_DIR", "/research/demo/models")
    monkeypatch.setenv("RK_RUNS_DIR", "/research/demo/runs")
    monkeypatch.setenv("RK_LOGS_DIR", "/research/demo/logs")

    paths = project_paths()

    assert paths.project_root.as_posix() == "/research/demo"
    assert paths.data_dir.as_posix() == "/research/demo/data"
    assert paths.models_dir.as_posix() == "/research/demo/models"
    assert paths.runs_dir.as_posix() == "/research/demo/runs"
    assert paths.logs_dir.as_posix() == "/research/demo/logs"


def test_project_paths_fail_without_rk_environment(monkeypatch):
    for key in list(os.environ):
        if key.startswith("RK_"):
            monkeypatch.delenv(key, raising=False)

    with pytest.raises(RuntimeError, match="RK_PROJECT_ROOT"):
        project_paths()

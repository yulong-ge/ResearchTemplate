"""Behavioral tests for the rendered BatchCom path contract."""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch


TEMPLATE = (
    Path(__file__).parents[1]
    / "rtmpl"
    / "templates"
    / "batchcom-research"
    / "src"
    / "paths.py"
)


def _load_paths(system: str) -> dict[str, object]:
    source = TEMPLATE.read_text(encoding="utf-8")
    source = source.replace("<proj>", "demo-project").replace("<conda-env>", "ml")
    namespace: dict[str, object] = {"__name__": "rendered_paths"}
    with patch("platform.system", return_value=system):
        exec(compile(source, str(TEMPLATE), "exec"), namespace)
    return namespace


def test_linux_paths_add_project_and_shared_data_model_roots():
    paths = _load_paths("Linux")
    research = Path("/home/dataset-assist-0/research")
    project = research / "demo-project"
    local_project = Path("/home/dataset-local/demo-project")

    assert paths["SHARED_DATA_ROOT"] == research / "_shared/data"
    assert paths["SHARED_MODEL_ROOT"] == research / "_shared/models"
    assert paths["DATA_ROOT"] == project / "data"
    assert paths["MODEL_ROOT"] == project / "models"
    assert paths["RESULTS_ROOT"] == project / "results"
    assert paths["DATA_CACHE"] == local_project / "data"
    assert paths["LIB_CACHE"] == Path("/home/dataset-local/cache")


def test_template_does_not_manage_project_or_framework_run_directories():
    paths = _load_paths("Linux")

    assert "RUNS_ROOT" not in paths
    assert "run_root" not in paths
    assert "SCRATCH_ROOT" not in paths
    assert "MODEL_CACHE" not in paths


def test_darwin_exposes_no_server_asset_or_cache_roots():
    paths = _load_paths("Darwin")

    for name in (
        "RESEARCH_ROOT",
        "SHARED_DATA_ROOT",
        "SHARED_MODEL_ROOT",
        "DATA_ROOT",
        "MODEL_ROOT",
        "RESULTS_ROOT",
        "LOCAL_ROOT",
        "DATA_CACHE",
        "LIB_CACHE",
    ):
        assert paths[name] is None

from pathlib import Path
import subprocess

from tests.test_cli_run import REPO_ROOT, write_config


def run_rk_doctor(cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "uv",
            "--cache-dir",
            str(REPO_ROOT / ".uv-cache"),
            "--project",
            str(REPO_ROOT),
            "run",
            "rk",
            "doctor",
        ],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def test_rk_doctor_reports_missing_config(tmp_path: Path):
    result = run_rk_doctor(tmp_path)

    assert result.returncode != 0
    assert ".rk/project.toml" in result.stderr


def test_rk_doctor_reports_project_config(tmp_path: Path):
    write_config(tmp_path)

    result = run_rk_doctor(tmp_path)

    assert result.returncode == 0
    assert "project=demo" in result.stdout
    assert "target=batchcom" in result.stdout
    assert f"canonical_root={tmp_path.as_posix()}" in result.stdout
    assert f"scratch_root={(tmp_path / 'scratch').as_posix()}" in result.stdout


def test_rk_doctor_rejects_template_placeholder(tmp_path: Path):
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

    result = run_rk_doctor(tmp_path)

    assert result.returncode == 1
    assert "replace CHANGE_ME" in result.stderr
    assert "Traceback" not in result.stderr

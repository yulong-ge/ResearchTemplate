import os
import json
from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]


def write_config(root: Path):
    config_dir = root / ".rk"
    config_dir.mkdir()
    (config_dir / "project.toml").write_text(
        f"""
[project]
name = "demo"
target = "batchcom"

[paths]
canonical_root = "{root.as_posix()}"
scratch_root = "{(root / 'scratch').as_posix()}"
data_dir = "{(root / 'data').as_posix()}"
models_dir = "{(root / 'models').as_posix()}"
runs_dir = "{(root / 'runs').as_posix()}"
logs_dir = "{(root / 'logs').as_posix()}"
""".strip(),
        encoding="utf-8",
    )


def run_rk(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "uv",
            "--cache-dir",
            str(REPO_ROOT / ".uv-cache"),
            "--project",
            str(REPO_ROOT),
            "run",
            "rk",
            *args,
        ],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=True,
    )


def run_rk_unchecked(cwd: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    child_env = os.environ.copy()
    if env:
        child_env.update(env)
    return subprocess.run(
        [
            "uv",
            "--cache-dir",
            str(REPO_ROOT / ".uv-cache"),
            "--project",
            str(REPO_ROOT),
            "run",
            "rk",
            *args,
        ],
        cwd=cwd,
        env=child_env,
        text=True,
        capture_output=True,
        check=False,
    )


def test_rk_run_executes_command_and_writes_manifest(tmp_path: Path):
    write_config(tmp_path)

    result = run_rk(
        tmp_path,
        "run",
        "python",
        "-c",
        "import os; print(os.environ['RK_ACTIVE_RUN']); print(os.environ['RK_PROJECT_ROOT'])",
    )

    assert "1" in result.stdout
    assert tmp_path.as_posix() in result.stdout

    manifest_files = list((tmp_path / "runs").glob("*/manifest.json"))
    assert len(manifest_files) == 1
    manifest = json.loads(manifest_files[0].read_text(encoding="utf-8"))
    assert manifest["project"] == "demo"
    assert manifest["target"] == "batchcom"
    assert manifest["command"][:3] == [
        "python",
        "-c",
        "import os; print(os.environ['RK_ACTIVE_RUN']); print(os.environ['RK_PROJECT_ROOT'])",
    ]
    assert manifest["returncode"] == 0


def test_rk_run_requires_command(tmp_path: Path):
    write_config(tmp_path)

    result = subprocess.run(
        [
            "uv",
            "--cache-dir",
            str(REPO_ROOT / ".uv-cache"),
            "--project",
            str(REPO_ROOT),
            "run",
            "rk",
            "run",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "rk run requires a command" in result.stderr


def test_rk_run_scratch_writes_manifest_to_scratch_root(tmp_path: Path):
    write_config(tmp_path)

    run_rk(tmp_path, "run", "--scratch", "python", "-c", "print('scratch')")

    canonical_manifest_files = list((tmp_path / "runs").glob("*/manifest.json"))
    scratch_manifest_files = list((tmp_path / "scratch" / "runs").glob("*/manifest.json"))
    assert canonical_manifest_files == []
    assert len(scratch_manifest_files) == 1
    manifest = json.loads(scratch_manifest_files[0].read_text(encoding="utf-8"))
    assert manifest["scratch"] is True
    assert manifest["returncode"] == 0


def test_rk_run_missing_launcher_writes_final_manifest(tmp_path: Path):
    write_config(tmp_path)

    result = run_rk_unchecked(tmp_path, "run", "definitely-missing-rk-launcher")

    assert result.returncode == 127
    assert "failed to start command" in result.stderr
    manifest_files = list((tmp_path / "runs").glob("*/manifest.json"))
    assert len(manifest_files) == 1
    manifest = json.loads(manifest_files[0].read_text(encoding="utf-8"))
    assert manifest["command"] == ["definitely-missing-rk-launcher"]
    assert manifest["returncode"] == 127


def test_rk_run_does_not_forward_wandb_identity_env(tmp_path: Path):
    write_config(tmp_path)

    result = run_rk_unchecked(
        tmp_path,
        "run",
        "python",
        "-c",
        "import os; print(os.environ.get('WANDB_RUN_ID')); print(os.environ.get('WANDB_RESUME'))",
        env={"WANDB_RUN_ID": "external-run", "WANDB_RESUME": "allow"},
    )

    assert result.returncode == 0
    assert result.stdout.splitlines() == ["None", "None"]


def test_rk_run_rejects_template_placeholder_without_traceback(tmp_path: Path):
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

    result = run_rk_unchecked(tmp_path, "run", "python", "-c", "print('never')")

    assert result.returncode == 1
    assert "replace CHANGE_ME" in result.stderr
    assert "Traceback" not in result.stderr

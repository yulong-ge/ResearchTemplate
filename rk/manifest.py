from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
import subprocess

from rk.config import ProjectConfig


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    project: str
    target: str
    command: list[str]
    cwd: str
    git_commit: str | None
    scratch: bool
    returncode: int | None = None


def current_git_commit(cwd: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def manifest_path(config: ProjectConfig, run_id: str, *, scratch: bool) -> Path:
    if scratch:
        return config.scratch_root / "runs" / run_id / "manifest.json"
    return config.runs_dir / run_id / "manifest.json"


def write_manifest(path: Path, manifest: RunManifest) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(asdict(manifest), indent=2, sort_keys=True)
    path.write_text(f"{content}\n", encoding="utf-8")

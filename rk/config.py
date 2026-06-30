from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


_PLACEHOLDER = "CHANGE_ME"


@dataclass(frozen=True)
class ProjectConfig:
    name: str
    target: str
    canonical_root: Path
    scratch_root: Path
    data_dir: Path
    models_dir: Path
    runs_dir: Path
    logs_dir: Path
    guard_mode: str = "strict"


def _reject_placeholder(label: str, value: str) -> None:
    if _PLACEHOLDER in value:
        raise ValueError(f"{label} contains CHANGE_ME; replace CHANGE_ME in .rk/project.toml")


def load_project_config(project_root: Path | str = ".") -> ProjectConfig:
    root = Path(project_root)
    path = root / ".rk" / "project.toml"
    if not path.exists():
        raise FileNotFoundError(f"missing required config: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data["project"]
    paths = data["paths"]
    guard = data.get("guard", {})
    for label, value in (
        ("project.name", project["name"]),
        ("paths.canonical_root", paths["canonical_root"]),
        ("paths.scratch_root", paths["scratch_root"]),
        ("paths.data_dir", paths["data_dir"]),
        ("paths.models_dir", paths["models_dir"]),
        ("paths.runs_dir", paths["runs_dir"]),
        ("paths.logs_dir", paths["logs_dir"]),
    ):
        _reject_placeholder(label, value)

    return ProjectConfig(
        name=project["name"],
        target=project.get("target", "batchcom"),
        canonical_root=Path(paths["canonical_root"]),
        scratch_root=Path(paths["scratch_root"]),
        data_dir=Path(paths["data_dir"]),
        models_dir=Path(paths["models_dir"]),
        runs_dir=Path(paths["runs_dir"]),
        logs_dir=Path(paths["logs_dir"]),
        guard_mode=guard.get("mode", "strict"),
    )

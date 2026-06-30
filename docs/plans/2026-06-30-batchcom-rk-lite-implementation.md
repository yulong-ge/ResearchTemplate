# batchcom RK-lite Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the batchcom-specific Git-first RK-lite direction while preserving the existing research workspace template as the baseline.

**Architecture:** Keep `rk` source in the framework repository root and keep copied projects free of `rk` source. Use `.rk/project.toml` as the project path source of truth, `rk run` as a transparent environment wrapper, and Git as the Mac/server code synchronization mechanism.

**Tech Stack:** Python 3.11+, `uv`, `pytest`, TOML via `tomllib`, shell/tmux execution, Markdown docs.

---

## Non-Negotiable Constraints

- Do not delete existing template files before evaluating their current behavior.
- Do not remove `templates/ara-research-workspace/scripts/remote_*.sh` in the first implementation pass. First document what they do and either keep them as legacy/fallback or ask for explicit removal.
- Do not move managed skills or OpenCode config out of the template without explicit confirmation.
- Use `batchcom`, not "Batch Camp".
- Do not add default Mutagen support in v1.
- Do not write SSH config or SSH MCP config from `rk` in v1.

### Task 1: Add Implementation ADR For RK-lite

**Files:**
- Create: `docs/adr/0002-batchcom-rk-lite.md`
- Read: `docs/plans/2026-06-30-batchcom-rk-lite-design.md`

**Step 1: Write the ADR**

Create `docs/adr/0002-batchcom-rk-lite.md`:

```markdown
# ADR 0002: batchcom Git-first RK-lite

## Status

Accepted.

## Context

The batchcom remote is the current target environment. The previous remote-sync design introduced too much complexity because Mac and server edits would conflict under one-way synchronization. The current direction is to use GitHub/Git as the code synchronization source of truth and keep `rk` as a small execution safety layer.

## Decision

Implement v1 as batchcom-specific RK-lite:

- code sync uses Git, not Mutagen
- `rk` source lives at the framework repository root
- copied projects contain `.rk/project.toml`, not `rk` source
- project `src/` is reserved for downstream research code
- `/home/dataset-assist-0/research/<project>` is canonical storage
- `/home/dataset-local/<project>` is optional explicit scratch storage
- SSH and SSH MCP configs are read-only inputs to `rk`

## Consequences

- The template remains simple and avoids multi-remote abstraction.
- Mac-local MCP tooling remains the primary rich agent environment.
- Server-side edits are allowed, but must use Git commit/push/pull.
- Future remotes can get separate designs when concrete requirements appear.
```

**Step 2: Verify**

Run:

```bash
rg -n "batchcom Git-first RK-lite|Mutagen|dataset-assist-0|project.toml" docs/adr/0002-batchcom-rk-lite.md
```

Expected: all four key terms are found.

**Step 3: Commit checkpoint**

Do not commit automatically unless the user has asked for commits. If commits are requested, commit only this ADR:

```bash
git add docs/adr/0002-batchcom-rk-lite.md
git commit -m "docs: record batchcom rk-lite architecture"
```

### Task 2: Correct Root Framework Documentation

**Files:**
- Modify: `AGENTS.md`
- Modify: `README.md`
- Modify: `docs/adr/0001-framework-template-split.md`
- Read: `docs/plans/2026-06-30-batchcom-rk-lite-design.md`

**Step 1: Update root `AGENTS.md`**

Replace the old runtime-location bullets:

```markdown
- The runtime command is named `rk`.
- Runtime source belongs inside `templates/ara-research-workspace/src/rk/` so copied projects can patch framework code locally.
- Generic execution logic should remain separate from target/server profiles.
- The template must support both `remote-sync` and `server-local` projects, without requiring migration between the two modes.
- Current concrete target priority is `batchcom`; do not hardcode it into generic runtime logic.
```

with:

```markdown
- The runtime command is named `rk`.
- `rk` source belongs at the framework repository root, not inside copied project templates.
- Copied projects contain `.rk/project.toml` and use `rk` as an external execution tool.
- The current v1 target is batchcom-specific, Git-first, and RK-lite.
- Do not generalize to multi-remote or Mutagen workflows until a concrete future remote requires it.
```

Add this rule under `Development Rules`:

```markdown
- Treat `templates/ara-research-workspace/` as a carefully designed baseline. Before deleting or replacing existing template artifacts, document what they do and ask for confirmation unless the deletion was explicitly approved.
```

**Step 2: Update root `README.md`**

In the layout block, add root `rk/` and remove `src/rk/` from the template description:

```text
rk/                              # RK-lite framework tool source
templates/
  ara-research-workspace/
    .rk/                         # Project-level rk config template
    src/                         # Downstream research code only
```

**Step 3: Update ADR 0001**

Change:

```markdown
The future `rk` runtime source lives inside the template at `templates/ara-research-workspace/src/rk/`.
```

to:

```markdown
ADR 0002 supersedes the original runtime placement: `rk` source lives at the framework repository root, while copied projects contain only project-level `.rk/` configuration.
```

**Step 4: Verify**

Run:

```bash
rg -n "src/rk|inside copied project|inside the template" AGENTS.md README.md docs/adr/0001-framework-template-split.md
```

Expected: no stale claim that `rk` source belongs inside the copied template. If matches remain, inspect them and keep only references that explicitly describe the obsolete design.

### Task 3: Scaffold Root Python Package For `rk`

**Files:**
- Create: `pyproject.toml`
- Create: `rk/__init__.py`
- Create: `rk/cli.py`
- Create: `rk/config.py`
- Create: `rk/env.py`
- Create: `rk/manifest.py`
- Create: `tests/test_config.py`
- Create: `tests/test_env.py`
- Create: `tests/test_cli_run.py`

**Step 1: Write failing config tests**

Create `tests/test_config.py`:

```python
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
```

**Step 2: Run failing test**

Run:

```bash
uv run pytest tests/test_config.py -q
```

Expected: FAIL because `rk.config` does not exist.

**Step 3: Add `pyproject.toml`**

Create `pyproject.toml`:

```toml
[project]
name = "skills-driven-ara-template"
version = "0.1.0"
description = "ResearchKit template framework and batchcom RK-lite execution tool"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
rk = "rk.cli:main"

[dependency-groups]
dev = [
  "pytest>=8.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 4: Add package init**

Create `rk/__init__.py`:

```python
"""RK-lite execution tooling for research workspace templates."""

__all__ = ["__version__"]

__version__ = "0.1.0"
```

**Step 5: Implement config loader**

Create `rk/config.py`:

```python
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib


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


def load_project_config(project_root: Path | str = ".") -> ProjectConfig:
    root = Path(project_root)
    path = root / ".rk" / "project.toml"
    if not path.exists():
        raise FileNotFoundError(f"missing required config: {path}")

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data["project"]
    paths = data["paths"]
    guard = data.get("guard", {})

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
```

**Step 6: Run config tests**

Run:

```bash
uv run pytest tests/test_config.py -q
```

Expected: PASS.

### Task 4: Implement Environment Injection

**Files:**
- Modify: `rk/env.py`
- Modify: `tests/test_env.py`

**Step 1: Write failing env tests**

Create `tests/test_env.py`:

```python
from pathlib import Path

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
    assert env["RK_DATA_DIR"] == "/home/dataset-assist-0/research/demo/data"
    assert env["RK_MODELS_DIR"] == "/home/dataset-assist-0/research/demo/models"
    assert env["RK_RUNS_DIR"] == "/home/dataset-assist-0/research/demo/runs"
    assert env["RK_LOGS_DIR"] == "/home/dataset-assist-0/research/demo/logs"
    assert env["RK_RUN_ID"] == "rk-20260630-abc123"
    assert env["RK_ACTIVE_RUN"] == "1"
    assert env["RK_SCRATCH"] == "0"
    assert env["WANDB_DIR"] == "/home/dataset-assist-0/research/demo/runs/rk-20260630-abc123/wandb"


def test_scratch_run_environment():
    env = build_run_environment(make_config(), run_id="rk-20260630-abc123", scratch=True)

    assert env["RK_SCRATCH"] == "1"
    assert env["RK_SCRATCH_RUN_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123"
    assert env["WANDB_DIR"] == "/home/dataset-local/demo/runs/rk-20260630-abc123/wandb"
```

**Step 2: Run failing env test**

Run:

```bash
uv run pytest tests/test_env.py -q
```

Expected: FAIL because `build_run_environment` does not exist.

**Step 3: Implement env builder**

Create `rk/env.py`:

```python
from __future__ import annotations

from pathlib import Path

from rk.config import ProjectConfig


def _as_posix(path: Path) -> str:
    return path.as_posix()


def build_run_environment(config: ProjectConfig, run_id: str, *, scratch: bool) -> dict[str, str]:
    canonical_run_dir = config.runs_dir / run_id
    scratch_run_dir = config.scratch_root / "runs" / run_id
    wandb_dir = (scratch_run_dir if scratch else canonical_run_dir) / "wandb"

    env = {
        "RK_ACTIVE_RUN": "1",
        "RK_RUN_ID": run_id,
        "RK_PROJECT_ROOT": _as_posix(config.canonical_root),
        "RK_DATA_DIR": _as_posix(config.data_dir),
        "RK_MODELS_DIR": _as_posix(config.models_dir),
        "RK_RUNS_DIR": _as_posix(config.runs_dir),
        "RK_LOGS_DIR": _as_posix(config.logs_dir),
        "RK_SCRATCH": "1" if scratch else "0",
        "RK_SCRATCH_RUN_DIR": _as_posix(scratch_run_dir),
        "WANDB_DIR": _as_posix(wandb_dir),
    }
    return env
```

**Step 4: Run env tests**

Run:

```bash
uv run pytest tests/test_env.py -q
```

Expected: PASS.

### Task 5: Implement Minimal `rk run`

**Files:**
- Modify: `rk/cli.py`
- Modify: `rk/manifest.py`
- Modify: `tests/test_cli_run.py`

**Step 1: Write CLI tests**

Create `tests/test_cli_run.py`:

```python
import json
from pathlib import Path
import subprocess


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


def test_rk_run_executes_command_and_writes_manifest(tmp_path: Path):
    write_config(tmp_path)

    result = subprocess.run(
        [
            "uv",
            "run",
            "rk",
            "run",
            "python",
            "-c",
            "import os; print(os.environ['RK_ACTIVE_RUN']); print(os.environ['RK_PROJECT_ROOT'])",
        ],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=True,
    )

    assert "1" in result.stdout
    assert tmp_path.as_posix() in result.stdout

    manifest_files = list((tmp_path / "runs").glob("*/manifest.json"))
    assert len(manifest_files) == 1
    manifest = json.loads(manifest_files[0].read_text(encoding="utf-8"))
    assert manifest["project"] == "demo"
    assert manifest["target"] == "batchcom"
    assert manifest["command"][:3] == ["python", "-c", "import os; print(os.environ['RK_ACTIVE_RUN']); print(os.environ['RK_PROJECT_ROOT'])"]
    assert manifest["returncode"] == 0
```

**Step 2: Run failing CLI test**

Run:

```bash
uv run pytest tests/test_cli_run.py -q
```

Expected: FAIL because `rk.cli` is not implemented.

**Step 3: Implement manifest helpers**

Create `rk/manifest.py`:

```python
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
import subprocess
from typing import Any

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
    path.write_text(json.dumps(asdict(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8")
```

**Step 4: Implement CLI**

Create `rk/cli.py`:

```python
from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from uuid import uuid4

from rk.config import load_project_config
from rk.env import build_run_environment
from rk.manifest import RunManifest, current_git_commit, manifest_path, write_manifest


def _new_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"rk-{stamp}-{uuid4().hex[:8]}"


def run_command(args: argparse.Namespace) -> int:
    if not args.command:
        print("rk run requires a command", file=sys.stderr)
        return 2

    project_root = Path.cwd()
    config = load_project_config(project_root)
    run_id = _new_run_id()
    env = os.environ.copy()
    env.update(build_run_environment(config, run_id=run_id, scratch=args.scratch))

    manifest_file = manifest_path(config, run_id, scratch=args.scratch)
    initial = RunManifest(
        run_id=run_id,
        project=config.name,
        target=config.target,
        command=args.command,
        cwd=project_root.as_posix(),
        git_commit=current_git_commit(project_root),
        scratch=args.scratch,
        returncode=None,
    )
    write_manifest(manifest_file, initial)

    completed = subprocess.run(args.command, cwd=project_root, env=env, check=False)
    final = RunManifest(
        run_id=run_id,
        project=config.name,
        target=config.target,
        command=args.command,
        cwd=project_root.as_posix(),
        git_commit=current_git_commit(project_root),
        scratch=args.scratch,
        returncode=completed.returncode,
    )
    write_manifest(manifest_file, final)
    return completed.returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rk")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    run = subparsers.add_parser("run")
    run.add_argument("--scratch", action="store_true")
    run.add_argument("command", nargs=argparse.REMAINDER)
    run.set_defaults(func=run_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 5: Run CLI tests**

Run:

```bash
uv run pytest tests/test_cli_run.py -q
```

Expected: PASS.

**Step 6: Run all root tests**

Run:

```bash
uv run pytest tests/ -q
```

Expected: PASS.

### Task 6: Add Template `.rk/project.toml`

**Files:**
- Create: `templates/ara-research-workspace/.rk/project.toml`
- Modify: `templates/ara-research-workspace/.gitignore`

**Step 1: Create template config directory and config**

Create `templates/ara-research-workspace/.rk/project.toml`:

```toml
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

[guard]
mode = "strict"
```

**Step 2: Preserve generated local state**

If `rk` later writes local state under `.rk/state/`, ignore it. Add to `templates/ara-research-workspace/.gitignore`:

```gitignore
.rk/state/
```

Do not ignore `.rk/project.toml`.

**Step 3: Verify**

Run:

```bash
rg -n "target = \"batchcom\"|canonical_root|guard" templates/ara-research-workspace/.rk/project.toml
```

Expected: all keys are present.

### Task 7: Update Template Docs Without Deleting Existing Workflow

**Files:**
- Modify: `templates/ara-research-workspace/AGENTS.md`
- Modify: root `README.md`
- Modify: `templates/ara-research-workspace/remote/README.md`
- Read: `templates/ara-research-workspace/scripts/remote_env.sh`
- Read: `templates/ara-research-workspace/scripts/remote_run.sh`
- Read: `templates/ara-research-workspace/scripts/remote_sync.sh`

**Step 1: Evaluate existing remote scripts**

Read each existing remote script and write a short section in `templates/ara-research-workspace/remote/README.md`:

```markdown
## Legacy Remote Scripts

The template still contains `scripts/remote_*.sh` from the previous remote framework. They are retained for now as reference/fallback while `rk` is introduced. New batchcom work should prefer `rk doctor`, `rk run`, `rk logs`, `rk stage`, and `rk collect`.

Do not delete these scripts without explicit confirmation.
```

**Step 2: Update template `AGENTS.md` storage rules**

Remove the stale line:

```markdown
- Framework runtime code lives in `src/rk/`.
```

Replace the remote execution section with a batchcom RK-lite section:

```markdown
### batchcom RK-lite Execution

- This project uses Git as the code synchronization source of truth between Mac and batchcom.
- Before editing, run `git status` and `git pull --ff-only`.
- Before meaningful training runs, prefer committed code. `rk run` records the commit hash in the run manifest.
- `rk` is an external framework tool; its source does not live in this project.
- Project path configuration lives in `.rk/project.toml`.
- Run commands through `rk run <launcher> ...` so `RK_*` paths, W&B local directory, logs, and manifests are set consistently.
- Store data, logs, outputs, checkpoints, and local W&B files under `$RK_PROJECT_ROOT` unless explicitly using `rk run --scratch`.
- Use `/home/dataset-assist-0/research/<project>` as canonical storage on batchcom.
- Use `/home/dataset-local/<project>` only for explicit high-performance scratch workflows with `rk stage` and `rk collect`.
- Do not assume server-local MCP parity with the Mac. Use the Mac for MCP-heavy literature and planning workflows.
```

Keep the existing research workflow, literature, experiments, ARA, and deep-learning discipline sections unless they directly conflict.

**Step 3: Update root `README.md`**

Human-facing template documentation belongs in the framework root `README.md`, not inside the copyable template. Remove `src/rk/` from the root layout block. Add `.rk/project.toml`:

```text
.rk/
  project.toml                    # batchcom RK-lite path and guard config
src/                              # Reusable code written during research
```

Add a short section:

```markdown
## batchcom Execution

This template is currently tuned for batchcom with Git-first synchronization and RK-lite execution. Code is synchronized through Git. `rk` is installed from the framework repository and is not copied into this project.

Default canonical project root on batchcom:

`/home/dataset-assist-0/research/<project>`

Optional scratch root:

`/home/dataset-local/<project>`
```

Delete `templates/ara-research-workspace/README.md` after the root README contains the template usage notes.

**Step 4: Verify stale `src/rk` references**

Run:

```bash
rg -n "src/rk|Framework runtime code lives" README.md templates/ara-research-workspace/AGENTS.md templates/ara-research-workspace/remote/README.md
test ! -e templates/ara-research-workspace/README.md
```

Expected: no stale instruction that copied projects contain `src/rk`.

### Task 8: Handle Misplaced `templates/.../src/rk` Scaffold Safely

**Files:**
- Read: `templates/ara-research-workspace/src/rk/README.md`
- Potentially delete: `templates/ara-research-workspace/src/rk/README.md`
- Potentially delete empty directory: `templates/ara-research-workspace/src/rk/`

**Step 1: Inspect scaffold**

Run:

```bash
sed -n '1,120p' templates/ara-research-workspace/src/rk/README.md
```

Expected: file is the misplaced scaffold saying framework runtime belongs there.

**Step 2: If it is only the scaffold, remove it**

This removal is explicitly approved by the design only if the file is just the misplaced `rk` runtime scaffold and contains no useful project-specific logic.

Run:

```bash
git diff -- templates/ara-research-workspace/src/rk/README.md
```

Expected: no user edits beyond the scaffold.

Then delete the file and remove the empty directory using `apply_patch` for the file deletion. Do not remove `templates/ara-research-workspace/src/.gitkeep`.

**Step 3: Verify**

Run:

```bash
find templates/ara-research-workspace/src -maxdepth 2 -type f | sort
```

Expected: `templates/ara-research-workspace/src/.gitkeep` remains; no `src/rk` files remain.

### Task 9: Add Project Path Helper Template

**Files:**
- Create: `templates/ara-research-workspace/src/project_paths.py`
- Create: `templates/ara-research-workspace/tests/test_project_paths.py`

**Step 1: Write path helper test**

Create `templates/ara-research-workspace/tests/test_project_paths.py`:

```python
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
```

**Step 2: Run failing template test**

Run:

```bash
cd templates/ara-research-workspace && uv run pytest tests/test_project_paths.py -q
```

Expected: FAIL because `src.project_paths` does not exist.

**Step 3: Implement helper**

Create `templates/ara-research-workspace/src/project_paths.py`:

```python
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
```

**Step 4: Run template path tests**

Run:

```bash
cd templates/ara-research-workspace && uv run pytest tests/test_project_paths.py -q
```

Expected: PASS.

### Task 10: Add `rk doctor` Minimal Checks

**Files:**
- Modify: `rk/cli.py`
- Create: `tests/test_cli_doctor.py`

**Step 1: Write doctor test**

Create `tests/test_cli_doctor.py`:

```python
from pathlib import Path
import subprocess


def test_rk_doctor_reports_missing_config(tmp_path: Path):
    result = subprocess.run(
        ["uv", "run", "rk", "doctor"],
        cwd=tmp_path,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert ".rk/project.toml" in result.stderr
```

**Step 2: Run failing doctor test**

Run:

```bash
uv run pytest tests/test_cli_doctor.py -q
```

Expected: FAIL because `doctor` command is not implemented.

**Step 3: Implement minimal doctor**

Add to `rk/cli.py`:

```python
def doctor_command(args: argparse.Namespace) -> int:
    try:
        config = load_project_config(Path.cwd())
    except FileNotFoundError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"project={config.name}")
    print(f"target={config.target}")
    print(f"canonical_root={config.canonical_root}")
    print(f"scratch_root={config.scratch_root}")
    return 0
```

Register:

```python
doctor = subparsers.add_parser("doctor")
doctor.set_defaults(func=doctor_command)
```

**Step 4: Run doctor tests**

Run:

```bash
uv run pytest tests/test_cli_doctor.py -q
```

Expected: PASS.

### Task 11: Final Verification

**Files:**
- All touched files.

**Step 1: Run root tests**

Run:

```bash
uv run pytest tests/ -q
```

Expected: all root `rk` tests pass.

**Step 2: Run template tests**

Run:

```bash
cd templates/ara-research-workspace && uv run pytest tests/ -q
```

Expected: template tests pass. If `uv` cannot run because the template has no `pyproject.toml`, either add a minimal template `pyproject.toml` in a separate reviewed task or run the specific test with a documented environment. Do not silently skip.

**Step 3: Check stale text**

Run:

```bash
rg -n "Batch Camp|src/rk|remote-sync|Mutagen" AGENTS.md README.md docs templates/ara-research-workspace -g '*.md' -g '*.toml'
```

Expected:

- no `Batch Camp`
- no stale instruction that copied projects contain `src/rk`
- Mutagen only appears as a non-goal or future possibility, not as a default v1 workflow
- remote-sync only appears as historical context or non-v1 text

**Step 4: Check git status**

Run:

```bash
git status --short
```

Expected: only intentional changes from this implementation pass plus the pre-existing repository restructuring changes.

**Step 5: Summarize residual risks**

Before marking implementation complete, summarize:

- which existing template scripts were kept
- whether any file deletion happened and why it was safe
- test commands and results
- any remaining unimplemented `rk` commands such as `logs`, `status`, `kill`, `stage`, `collect`

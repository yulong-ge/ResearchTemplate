from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

from rk.config import load_project_config
from rk.env import build_run_environment
from rk.manifest import RunManifest, current_git_commit, manifest_path, write_manifest


_WANDB_IDENTITY_ENV = (
    "WANDB_RUN_ID",
    "WANDB_RESUME",
    "WANDB_NAME",
)


def _new_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"rk-{stamp}-{uuid4().hex[:8]}"


def _base_child_environment() -> dict[str, str]:
    env = os.environ.copy()
    for name in _WANDB_IDENTITY_ENV:
        env.pop(name, None)
    return env


def _load_config_or_report(project_root: Path):
    try:
        return load_project_config(project_root)
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return None


def run_command(args: argparse.Namespace) -> int:
    if not args.command:
        print("rk run requires a command", file=sys.stderr)
        return 2

    project_root = Path.cwd()
    config = _load_config_or_report(project_root)
    if config is None:
        return 1
    run_id = _new_run_id()
    env = _base_child_environment()
    env.update(build_run_environment(config, run_id=run_id, scratch=args.scratch))
    git_commit = current_git_commit(project_root)

    manifest_file = manifest_path(config, run_id, scratch=args.scratch)
    initial = RunManifest(
        run_id=run_id,
        project=config.name,
        target=config.target,
        command=args.command,
        cwd=project_root.as_posix(),
        git_commit=git_commit,
        scratch=args.scratch,
        returncode=None,
    )
    write_manifest(manifest_file, initial)

    try:
        completed = subprocess.run(args.command, cwd=project_root, env=env, check=False)
        returncode = completed.returncode
    except OSError as exc:
        print(f"failed to start command: {exc}", file=sys.stderr)
        returncode = 127

    final = RunManifest(
        run_id=run_id,
        project=config.name,
        target=config.target,
        command=args.command,
        cwd=project_root.as_posix(),
        git_commit=git_commit,
        scratch=args.scratch,
        returncode=returncode,
    )
    write_manifest(manifest_file, final)
    return returncode


def doctor_command(args: argparse.Namespace) -> int:
    config = _load_config_or_report(Path.cwd())
    if config is None:
        return 1

    print(f"project={config.name}")
    print(f"target={config.target}")
    print(f"canonical_root={config.canonical_root}")
    print(f"scratch_root={config.scratch_root}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rk")
    subparsers = parser.add_subparsers(dest="command_name", required=True)

    doctor = subparsers.add_parser("doctor")
    doctor.set_defaults(func=doctor_command)

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

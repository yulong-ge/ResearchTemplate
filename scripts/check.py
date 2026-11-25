"""Run framework checks against the worktree or a formatted Git index."""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "node_modules" / ".bin"
PRESERVED = (
    ".agents/notes/archived/",
    "docs/adr/",
    "docs/plans/",
    "docs/research/",
    "rtmpl/templates/",
)
PRETTIER = (".md", ".json", ".jsonc", ".yaml", ".yml")
HOOKS = (".githooks/pre-commit", ".githooks/pre-push")


def run(*args, cwd=ROOT):
    subprocess.run(args, cwd=cwd, check=True)


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def active_files(root, paths):
    return sorted(
        path
        for path in paths
        if path
        and not path.startswith(PRESERVED)
        and (root / path).is_file()
        and not (root / path).is_symlink()
    )


def checks(root, paths, *, format_files=False):
    files = active_files(root, paths)
    python = [path for path in files if path.endswith(".py")]
    markup = [path for path in files if path.endswith(PRETTIER)]
    markdown = [path for path in markup if path.endswith(".md")]
    toml = [path for path in files if path.endswith(".toml")]

    if python:
        run(
            "ruff",
            "format",
            *([] if format_files else ["--check"]),
            "--",
            *python,
            cwd=root,
        )
    if markup:
        run(
            BIN / "prettier",
            "--write" if format_files else "--check",
            "--",
            *markup,
            cwd=root,
        )
    if toml:
        run(
            BIN / "taplo",
            "fmt",
            *([] if format_files else ["--check"]),
            *toml,
            cwd=root,
        )

    if not format_files:
        run("ruff", "check", "rtmpl", "tests", "scripts", cwd=root)
        if markdown:
            run(BIN / "markdownlint-cli2", *markdown, cwd=root)
        for hook in HOOKS:
            run("sh", "-n", hook, cwd=root)
        run(sys.executable, "-m", "pytest", cwd=root)


def staged():
    if (
        subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", "HEAD"],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
        ).returncode
        == 0
    ):
        excluded = [f"!{prefix}*" for prefix in PRESERVED]
        for formatter, extensions in (
            ("ruff format --stdin-filename {} -", (".py",)),
            ("prettier --stdin-filepath {}", PRETTIER),
            ("taplo fmt -", (".toml",)),
        ):
            run(
                "git",
                "-c",
                "core.quotePath=false",
                "format-staged",
                "--formatter",
                formatter,
                *(f"*{extension}" for extension in extensions),
                *excluded,
            )
    else:
        print("Initial commit: checking the index as staged.", flush=True)

    paths = os.fsdecode(git("ls-files", "--cached", "-z")).split("\0")
    with TemporaryDirectory(prefix="rtmpl-index-") as snapshot:
        run("git", "checkout-index", "--all", f"--prefix={snapshot}/")
        checks(Path(snapshot), paths)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode", choices=("check", "format", "staged"), nargs="?", default="check"
    )
    args = parser.parse_args()
    os.environ["PATH"] = os.pathsep.join((str(BIN), os.environ["PATH"]))
    try:
        if args.mode == "staged":
            staged()
        else:
            paths = os.fsdecode(
                git("ls-files", "--cached", "--others", "--exclude-standard", "-z")
            ).split("\0")
            checks(ROOT, set(paths), format_files=args.mode == "format")
    except subprocess.CalledProcessError as exc:
        command = Path(exc.cmd[0]).name
        print(f"{command} failed with exit code {exc.returncode}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

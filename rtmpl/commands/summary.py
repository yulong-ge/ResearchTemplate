"""rtmpl summary — rebuild and optionally open the HTML dashboard."""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from ._common import CommandError, require_project_root

_BUILDER = "src/dashboard_builder.py"
_DASHBOARD = "to_human/dashboard.html"


def run(args) -> int:
    root = require_project_root(Path.cwd())
    builder = root / _BUILDER
    if not builder.is_file():
        raise CommandError(
            f"{_BUILDER} is missing — the project template does not ship a dashboard builder"
        )
    result = subprocess.run(
        ["uv", "run", "python", _BUILDER],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CommandError(
            f"dashboard builder failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )
    dashboard = root / _DASHBOARD
    if not dashboard.is_file():
        raise CommandError(f"dashboard builder ran but {_DASHBOARD} was not produced")
    print(f"Dashboard: {dashboard}")
    if getattr(args, "open", False):
        opener = "open" if sys.platform == "darwin" else (shutil.which("xdg-open") or "open")
        subprocess.Popen([opener, str(dashboard)])
    return 0

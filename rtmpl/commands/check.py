"""`rtmpl check` — validate a project's research record contract."""
from __future__ import annotations

from pathlib import Path

from ..core.research import validate_project
from ._common import CommandError


def run(args) -> int:
    errors = validate_project(Path.cwd())
    if errors:
        details = "\n".join(f"  - {error}" for error in errors)
        raise CommandError(f"research contract check failed:\n{details}")
    print("Research contract: OK")
    return 0

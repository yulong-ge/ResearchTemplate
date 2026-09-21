"""rtmpl check — validate a project's research record contract."""
from __future__ import annotations

from pathlib import Path

from ..core.consistency import validate_consistency
from ..core.research import validate_project
from ._common import CommandError


def run(args) -> int:
    if getattr(args, "consistency", False):
        errors = validate_consistency(Path.cwd())
        label = "Research consistency"
    else:
        errors = validate_project(Path.cwd())
        label = "Research contract"
    if errors:
        details = "\n".join(f"  - {error}" for error in errors)
        raise CommandError(f"{label.lower()} check failed:\n{details}")
    print(f"{label}: OK")
    return 0

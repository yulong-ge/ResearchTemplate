"""rtmpl check — validate a project's research record contract."""
from __future__ import annotations

from pathlib import Path

from ..core.consistency import validate_consistency
from ..core.research import validate_project
from ._common import CommandError, require_project_root


def run(args) -> int:
    root = require_project_root(Path.cwd())
    if getattr(args, "consistency", False):
        errors = validate_consistency(root)
        label = "Research consistency"
    else:
        errors = validate_project(root)
        label = "Research contract"
    if errors:
        details = "\n".join(f"  - {error}" for error in errors)
        raise CommandError(f"{label.lower()} check failed:\n{details}")
    print(f"{label}: OK")
    return 0

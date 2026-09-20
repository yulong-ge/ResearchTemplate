"""`rtmpl resume` — print the smallest useful research handoff."""
from __future__ import annotations

from pathlib import Path

from ..core.research import resume_text
from ._common import CommandError


def run(args) -> int:
    try:
        print(resume_text(Path.cwd()))
    except (FileNotFoundError, ValueError) as exc:
        raise CommandError(str(exc)) from exc
    return 0

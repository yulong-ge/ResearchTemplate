"""rtmpl resume — print the smallest useful research handoff.

If to_human/paused-context.md exists it is printed first, then the normal
compact handoff. The file is deliberately not auto-deleted: the human/agent
decides when the captured context has been fully absorbed.
"""
from __future__ import annotations

from pathlib import Path

from ..core.research import PAUSED_CONTEXT, resume_text
from ._common import CommandError, require_project_root


def run(args) -> int:
    root = require_project_root(Path.cwd())
    try:
        text = resume_text(root)
    except (FileNotFoundError, ValueError) as exc:
        raise CommandError(str(exc)) from exc
    paused = root / PAUSED_CONTEXT
    if paused.is_file():
        print(paused.read_text(encoding="utf-8").strip())
        print()
        print("---")
        print()
    print(text)
    return 0

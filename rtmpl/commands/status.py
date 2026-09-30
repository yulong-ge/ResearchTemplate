"""`rtmpl status` — show a read-only template update plan."""
from __future__ import annotations

from pathlib import Path

from . import update as update_cmd


def run(args) -> int:
    plan = update_cmd.build_plan(args, Path.cwd())
    update_cmd.print_plan(plan, as_json=getattr(args, "json", False))
    return 0

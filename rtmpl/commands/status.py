"""`rtmpl status` — show pending changes (= `rtmpl update --dry-run`)."""
from __future__ import annotations


def run(args) -> int:
    from . import update as update_cmd

    args.dry_run = True
    return update_cmd.run(args)

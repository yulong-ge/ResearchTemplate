"""rtmpl CLI entry point."""
from __future__ import annotations

import argparse
import os
import sys

from . import __version__
from .commands import adopt, check, list as list_cmd, new, repair, resume, status, update
from .commands._common import CommandError
from .core.update_check import latest_known_version, staleness_banner


def _parse_var(items) -> dict[str, str]:
    out: dict[str, str] = {}
    for it in items or []:
        if "=" not in it:
            raise SystemExit(f"invalid --var {it!r}; expected field=value")
        k, v = it.split("=", 1)
        out[k.strip()] = v
    return out


def _add_project_creation_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("name", help="project name (proj variable + default dir)")
    parser.add_argument("--template", "-t")
    parser.add_argument("--path", help="target directory (default: ./<name>)")
    parser.add_argument("--var", action="append", default=[], metavar="field=value")
    parser.add_argument("--no-input", action="store_true")
    parser.add_argument("--force", action="store_true")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rtmpl", description="Research-project template sync CLI.")
    p.add_argument("--version", action="version", version=f"rtmpl {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("list", help="list available templates")
    sp.set_defaults(func=list_cmd.run)

    for name in ("new", "init"):
        sp = sub.add_parser(name, help="create a new project from a template")
        _add_project_creation_args(sp)
        sp.set_defaults(func=new.run)

    sp = sub.add_parser("update", help="sync template updates into the current project")
    sp.add_argument("--force", action="store_true")
    sp.add_argument("--skip", action="store_true")
    sp.add_argument("--dry-run", action="store_true")
    sp.add_argument("--no-input", action="store_true")
    sp.add_argument("--allow-downgrade", action="store_true")
    sp.set_defaults(func=update.run)

    sp = sub.add_parser("adopt", help="bring an existing cp project under rtmpl management")
    sp.add_argument("--template", "-t")
    sp.add_argument("--var", action="append", default=[], metavar="field=value")
    sp.add_argument("--no-input", action="store_true")
    sp.add_argument("--repair", action="store_true")
    sp.set_defaults(func=adopt.run)

    sp = sub.add_parser("status", help="show pending changes (= update --dry-run)")
    sp.set_defaults(func=status.run)

    sp = sub.add_parser("resume", help="show the compact research handoff")
    sp.set_defaults(func=resume.run)

    sp = sub.add_parser("check", help="validate the research record contract")
    sp.set_defaults(func=check.run)

    sp = sub.add_parser("repair", help="rebuild .rtmpl/state.json from disk")
    sp.add_argument("--template", "-t")
    sp.set_defaults(func=repair.run)

    return p


def _print_staleness_banner() -> None:
    """Warn on stderr when the installed rtmpl is behind the template repo.

    Never blocks execution and never demands network: offline / CI /
    RTMPL_NO_UPDATE_CHECK=1 degrade to silence.
    """
    if os.environ.get("RTMPL_NO_UPDATE_CHECK", "") not in ("", "0", "false", "False"):
        return
    try:
        latest = latest_known_version(__version__)
    except Exception:
        return
    banner = staleness_banner(__version__, latest)
    if banner:
        print(banner, file=sys.stderr)


def main(argv=None) -> int:
    _print_staleness_banner()
    parser = build_parser()
    args = parser.parse_args(argv)
    if hasattr(args, "var"):
        args.var = _parse_var(args.var)
    try:
        return args.func(args) or 0
    except CommandError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

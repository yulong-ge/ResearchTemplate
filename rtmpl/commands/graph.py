"""rtmpl graph — print the evolution diagram, or render it to an image.

Default mode writes to_human/evolution.mmd to stdout: Mermaid source is
human-readable and can be pasted into any renderer. --render <file> renders
to png/svg/pdf via mmdc (mermaid-cli) when installed, else via
npx --yes @mermaid-js/mermaid-cli. A missing renderer is an explicit
error — the diagram is never silently skipped.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from ._common import CommandError, require_project_root

_EVOLUTION = "to_human/evolution.mmd"
_RENDER_EXTS = {".png", ".svg", ".pdf"}


def _render_cmd(mmd: Path, out: Path) -> list[str]:
    if mmdc := shutil.which("mmdc"):
        return [mmdc, "-i", str(mmd), "-o", str(out)]
    if npx := shutil.which("npx"):
        return [
            npx,
            "--yes",
            "@mermaid-js/mermaid-cli",
            "-i",
            str(mmd),
            "-o",
            str(out),
        ]
    raise CommandError(
        "cannot render: neither mmdc nor npx found on PATH "
        "(install @mermaid-js/mermaid-cli, or run rtmpl graph without --render "
        "and paste the Mermaid source into a renderer)"
    )


def run(args) -> int:
    root = require_project_root(Path.cwd())
    mmd = root / _EVOLUTION
    if not mmd.is_file():
        raise CommandError(f"{_EVOLUTION} is missing — run inside a research project")

    out = getattr(args, "render", None)
    if out is None:
        print(mmd.read_text(encoding="utf-8"), end="")
        return 0

    out_path = Path(out)
    if out_path.suffix.lower() not in _RENDER_EXTS:
        raise CommandError(
            f"--render target must end in one of {sorted(_RENDER_EXTS)} (got {out!r})"
        )
    result = subprocess.run(
        _render_cmd(mmd, out_path),
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise CommandError(
            f"mermaid render failed (exit {result.returncode}):\n{result.stderr.strip()}"
        )
    if not out_path.is_file():
        raise CommandError(f"renderer ran but {out} was not produced")
    print(f"Rendered: {out_path}")
    return 0

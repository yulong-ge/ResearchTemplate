"""`rtmpl list` — list available templates."""
from __future__ import annotations

from ..core.template import list_templates, load_manifest


def run(args) -> int:
    names = list_templates()
    if not names:
        print("(no templates installed)")
        return 0
    for n in names:
        m = load_manifest(n)
        print(f"{m.name} — {m.display} (v{m.version})")
    return 0

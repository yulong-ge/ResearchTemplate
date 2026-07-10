"""Template-version skew policy (plan §3.4).

``template_version`` lives only in ``state.json``. ``update`` compares the
installed tool's template ``version`` against the project's version: forward →
proceed; equal → still classify (no abort); older → abort unless
``--allow-downgrade``.
"""
from __future__ import annotations

import re

FORWARD = "forward"
EQUAL = "equal"
DOWNGRADE = "downgrade"


def _vtuple(v: str) -> tuple[int, ...]:
    parts: list[int] = []
    for chunk in v.split("."):
        m = re.match(r"\d+", chunk)
        parts.append(int(m.group()) if m else 0)
    return tuple(parts)


def compare(tool_version: str, project_version: str) -> str:
    """Return FORWARD / EQUAL / DOWNGRADE for tool-vs-project."""
    a, b = _vtuple(tool_version), _vtuple(project_version)
    if a > b:
        return FORWARD
    if a == b:
        return EQUAL
    return DOWNGRADE

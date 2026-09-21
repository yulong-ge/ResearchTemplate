"""rtmpl pause — capture interruption context for the next resume."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ..core.research import PAUSED_CONTEXT, load_state, validate_state
from ._common import CommandError, require_project_root


def run(args) -> int:
    root = require_project_root(Path.cwd())
    try:
        state = load_state(root)
    except FileNotFoundError as exc:
        raise CommandError(
            "cannot pause: research-state.yaml is missing — run inside a research project"
        ) from exc
    except ValueError as exc:
        raise CommandError(f"cannot pause: {exc}") from exc
    errors = validate_state(state)
    if errors:
        details = "; ".join(errors)
        raise CommandError(f"cannot pause: research-state.yaml is invalid: {details}")

    timestamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    next_action = state["next_action"]
    waiting = state.get("waiting") or {}
    lines = [
        "# Paused context",
        "",
        f"Paused at: {timestamp}",
        "",
        "## In progress",
        "",
        f"- Status: {state['status']}",
        f"- Direction: {state.get('active_direction') or 'none'}",
        f"- Hypothesis: {state.get('active_hypothesis') or 'none'}",
        "",
        "## Next intended action",
        "",
        f"- Owner: {next_action['owner']}",
        f"- Action: {next_action['text']}",
        f"- Done when: {next_action['done_when']}",
        "",
        "## Waiting / blockers",
        "",
        f"- Reason: {waiting.get('reason') or 'none'}",
        f"- On: {waiting.get('on') or 'none'}",
        f"- Unblock action: {waiting.get('unblock_action') or 'none'}",
        "",
        "## Open notes",
        "",
        "- <unwritten thoughts, half-formed ideas, or context to reload>",
        "",
    ]
    target = root / PAUSED_CONTEXT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("\n".join(lines), encoding="utf-8")
    print(f"Paused context written to {PAUSED_CONTEXT}")
    return 0

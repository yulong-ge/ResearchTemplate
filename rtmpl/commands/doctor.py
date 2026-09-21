"""rtmpl doctor — health check a research project's seed records."""
from __future__ import annotations

from pathlib import Path

from ..core.research import (
    POLICY_FILE,
    REQUIRED_RECORDS,
    RESEARCH_STATE,
    load_policy,
    load_state,
    validate_policy,
    validate_state,
)
from ._common import CommandError, require_project_root

_PLACEHOLDERS = ("<one-line research question>", "<one concrete next action>")


def run(args) -> int:
    root = require_project_root(Path.cwd())
    failures: list[str] = []

    for rel in REQUIRED_RECORDS:
        if not (root / rel).is_file():
            failures.append(f"missing required record: {rel}")

    state_ok = False
    try:
        state = load_state(root)
    except FileNotFoundError:
        failures.append(f"{RESEARCH_STATE} is missing")
    except ValueError as exc:
        failures.append(str(exc))
    else:
        state_errors = validate_state(state)
        failures.extend(state_errors)
        state_ok = not state_errors
        if state_ok:
            question = state.get("research_question")
            if not isinstance(question, str) or not question.strip() or question.strip() in _PLACEHOLDERS:
                failures.append(
                    f"{RESEARCH_STATE}: research_question still holds the template placeholder — "
                    "replace it with the real one-line question"
                )
            text = (state.get("next_action") or {}).get("text")
            if not isinstance(text, str) or not text.strip() or text.strip() in _PLACEHOLDERS:
                failures.append(
                    f"{RESEARCH_STATE}: next_action.text still holds the template placeholder — "
                    "replace it with one concrete action"
                )

    try:
        policy = load_policy(root)
    except FileNotFoundError:
        failures.append(f"{POLICY_FILE} is missing")
    except ValueError as exc:
        failures.append(str(exc))
    else:
        failures.extend(validate_policy(policy))

    if failures:
        details = "\n".join(f"  - {f}" for f in failures)
        raise CommandError(f"doctor found {len(failures)} problem(s):\n{details}")
    print("Doctor: all checks pass")
    return 0

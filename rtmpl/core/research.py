"""Research-record contract shared by the resume and check commands."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

RESEARCH_STATE = "research-state.yaml"
RESUME_FILE = "to_human/latest.md"
POLICY_FILE = "research/policy.yaml"
REQUIRED_RECORDS = (
    RESEARCH_STATE,
    RESUME_FILE,
    "hypotheses.md",
    "research-log.md",
    "findings.md",
    "claims.md",
    "decisions.md",
    "research/policy.yaml",
    "to_human/evolution.mmd",
    "to_human/evidence.mmd",
    "to_human/trajectory.csv",
)
STATUSES = {"candidate", "active", "waiting", "closed"}
LOOP_MODES = {"auto", "human", "inherit_policy"}
POLICY_LOOP_MODES = {"auto", "human"}
OBJECT_PREFIXES = {
    "hypotheses": "H",
    "experiments": "E",
    "results": "R",
    "findings": "F",
    "claims": "C",
    "decisions": "D",
}
RELATION_TYPES = {
    "tested_by",
    "produced",
    "supports",
    "challenges",
    "authorizes",
    "follows",
}
_ID_RE = re.compile(r"^[A-Z][A-Za-z0-9._-]*$")


def load_state(project_root: Path) -> dict[str, Any]:
    """Load the project research state and fail with its parsing context."""
    path = project_root / RESEARCH_STATE
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return payload


def load_policy(project_root: Path) -> dict[str, Any]:
    """Load the project policy used to resolve inherited loop modes."""
    path = project_root / POLICY_FILE
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise
    except yaml.YAMLError as exc:
        raise ValueError(f"{path}: invalid YAML: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return payload


def validate_state(data: dict[str, Any]) -> list[str]:
    """Return actionable contract errors without changing project files."""
    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("research-state.yaml: schema_version must be 1")
    if data.get("status") not in STATUSES:
        errors.append("research-state.yaml: status must be candidate, active, waiting, or closed")

    loop_control = data.get("loop_control")
    if not isinstance(loop_control, dict):
        errors.append("research-state.yaml: loop_control must be a mapping")
    else:
        for name in ("inner", "outer"):
            if loop_control.get(name) not in LOOP_MODES:
                errors.append(f"research-state.yaml: loop_control.{name} has an invalid mode")

    next_action = data.get("next_action")
    if not isinstance(next_action, dict):
        errors.append("research-state.yaml: next_action must be a mapping")
    else:
        if next_action.get("owner") not in {"agent", "human"}:
            errors.append("research-state.yaml: next_action.owner must be agent or human")
        if not isinstance(next_action.get("text"), str) or not next_action["text"].strip():
            errors.append("research-state.yaml: next_action.text must be non-empty")
        if not isinstance(next_action.get("done_when"), str) or not next_action["done_when"].strip():
            errors.append("research-state.yaml: next_action.done_when must be non-empty")

    waiting = data.get("waiting")
    if not isinstance(waiting, dict):
        errors.append("research-state.yaml: waiting must be a mapping")

    objects = data.get("objects")
    object_ids: set[str] = set()
    if not isinstance(objects, dict):
        errors.append("research-state.yaml: objects must be a mapping")
    else:
        for key, prefix in OBJECT_PREFIXES.items():
            values = objects.get(key)
            if not isinstance(values, list):
                errors.append(f"research-state.yaml: objects.{key} must be a list")
                continue
            for value in values:
                if not isinstance(value, str) or not _ID_RE.fullmatch(value) or not value.startswith(prefix):
                    errors.append(f"research-state.yaml: objects.{key} contains invalid ID {value!r}")
                elif value in object_ids:
                    errors.append(f"research-state.yaml: duplicate object ID {value}")
                else:
                    object_ids.add(value)

    for field, prefix in (("active_direction", "D"), ("active_hypothesis", "H")):
        value = data.get(field)
        if value is not None and (not isinstance(value, str) or not value.startswith(prefix)):
            errors.append(f"research-state.yaml: {field} must be a {prefix} ID or null")
        elif value is not None and value not in object_ids:
            errors.append(f"research-state.yaml: {field} points to unknown ID {value}")

    relations = data.get("relations")
    if not isinstance(relations, list):
        errors.append("research-state.yaml: relations must be a list")
    else:
        for index, relation in enumerate(relations, start=1):
            if not isinstance(relation, dict):
                errors.append(f"research-state.yaml: relation {index} must be a mapping")
                continue
            source = relation.get("from")
            target = relation.get("to")
            relation_type = relation.get("type")
            if source not in object_ids:
                errors.append(f"research-state.yaml: relation {index} has unknown from ID {source!r}")
            if target not in object_ids:
                errors.append(f"research-state.yaml: relation {index} has unknown to ID {target!r}")
            if relation_type not in RELATION_TYPES:
                errors.append(f"research-state.yaml: relation {index} has invalid type {relation_type!r}")
    return errors


def validate_policy(data: dict[str, Any]) -> list[str]:
    """Validate the policy fields that affect loop execution."""
    errors: list[str] = []
    loop_control = data.get("loop_control")
    if not isinstance(loop_control, dict):
        return ["research/policy.yaml: loop_control must be a mapping"]
    for name in ("inner", "outer"):
        if loop_control.get(name) not in POLICY_LOOP_MODES:
            errors.append(f"research/policy.yaml: loop_control.{name} must be auto or human")
    return errors


def validate_project(project_root: Path) -> list[str]:
    """Validate required record homes and the compact state contract."""
    errors: list[str] = []
    for rel in REQUIRED_RECORDS:
        if not (project_root / rel).is_file():
            errors.append(f"missing required research record: {rel}")
    try:
        state = load_state(project_root)
    except FileNotFoundError:
        return errors
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    errors.extend(validate_state(state))
    try:
        policy = load_policy(project_root)
    except FileNotFoundError:
        return errors
    except ValueError as exc:
        errors.append(str(exc))
        return errors
    errors.extend(validate_policy(policy))
    return errors


def resume_text(project_root: Path) -> str:
    """Render a concise resume header followed by the human-maintained brief."""
    state = load_state(project_root)
    errors = validate_state(state)
    if errors:
        raise ValueError("; ".join(errors))
    policy = load_policy(project_root)
    policy_errors = validate_policy(policy)
    if policy_errors:
        raise ValueError("; ".join(policy_errors))
    latest = (project_root / RESUME_FILE).read_text(encoding="utf-8").strip()
    if not latest:
        raise ValueError(f"{project_root / RESUME_FILE}: file is empty")
    state_loop_control = state["loop_control"]
    policy_loop_control = policy["loop_control"]
    loop_control = {
        name: (
            state_loop_control[name]
            if state_loop_control[name] != "inherit_policy"
            else policy_loop_control[name]
        )
        for name in ("inner", "outer")
    }
    next_action = state["next_action"]
    waiting = state["waiting"]
    header = [
        f"Status: {state['status']}",
        f"Direction: {state.get('active_direction') or 'none'}",
        f"Hypothesis: {state.get('active_hypothesis') or 'none'}",
        f"Loop: inner={loop_control['inner']} outer={loop_control['outer']}",
        f"Next: {next_action['text']} ({next_action['owner']}; done when: {next_action['done_when']})",
        f"Waiting: {waiting.get('reason') or 'none'}",
        "",
        latest,
    ]
    return "\n".join(header)

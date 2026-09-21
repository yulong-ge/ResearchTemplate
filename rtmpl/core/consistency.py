"""File-existence consistency checks behind ``rtmpl check --consistency``.

The base contract check validates research-state.yaml shapes; this pass proves
the IDs and links it names actually resolve on disk. Every error pairs the
problem with the concrete fix so an agent can act without guessing.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .research import (
    EXPERIMENT_LABEL_RE,
    RESEARCH_STATE,
    load_policy,
    load_state,
    validate_policy,
    validate_state,
)

# Record file that owns each object kind's full text. Experiments resolve to a
# directory instead of a single record; results resolve to experiment result.md
# files, so they are checked separately.
_RECORD_FOR_KIND = {
    "hypotheses": "hypotheses.md",
    "findings": "findings.md",
    "claims": "claims.md",
    "decisions": "decisions.md",
}
_EXPERIMENT_EXCLUDES = {"_template", "README.md"}
_MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
_HEADING_RE = re.compile(r"^#{1,6}\s+")
_REF_TOKEN_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_YAML_BLOCK_RE = re.compile(r"\`\`\`yaml\n(.*?)\`\`\`", re.DOTALL)


def _object_sections(record_path: Path) -> set[str]:
    """Collect object ids declared as headings or yaml 'id:' keys in a record."""
    ids: set[str] = set()
    try:
        text = record_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ids
    for line in text.splitlines():
        match = _HEADING_RE.match(line)
        if match:
            heading = line[match.end():].strip()
            token = heading.split(":", 1)[0].strip()
            if token:
                ids.add(token)
    for block in _YAML_BLOCK_RE.findall(text):
        try:
            payload = yaml.safe_load(block)
        except yaml.YAMLError:
            continue
        if isinstance(payload, dict) and isinstance(payload.get("id"), str):
            ids.add(payload["id"])
    return ids


def _check_objects_resolve(root: Path, objects: dict[str, Any], errors: list[str]) -> None:
    for kind, rel in _RECORD_FOR_KIND.items():
        values = objects.get(kind) or []
        declared = _object_sections(root / rel)
        for value in values:
            if not isinstance(value, str):
                continue
            if value not in declared:
                errors.append(
                    f"objects.{kind}: {value} is not declared in {rel} "
                    f"(add a '## {value}: ...' section with an 'id: {value}' yaml block, "
                    f"or remove it from research-state.yaml)"
                )
    # Results live in experiments/<label>/result.md yaml blocks.
    declared_results: set[str] = set()
    experiments_dir = root / "experiments"
    if experiments_dir.is_dir():
        for result_file in experiments_dir.glob("*/result.md"):
            declared_results |= _object_sections(result_file)
    for value in objects.get("results") or []:
        if isinstance(value, str) and value not in declared_results:
            errors.append(
                f"objects.results: {value} is not declared in any experiments/*/result.md "
                f"(add an 'id: {value}' yaml block to the owning experiment's result.md, "
                f"or remove it from research-state.yaml)"
            )


def _check_experiment_dirs(root: Path, objects: dict[str, Any], errors: list[str]) -> None:
    labels = set(objects.get("experiments") or [])
    experiments_dir = root / "experiments"
    on_disk = (
        {p.name for p in experiments_dir.iterdir() if p.is_dir()}
        if experiments_dir.is_dir()
        else set()
    ) - _EXPERIMENT_EXCLUDES
    for label in sorted(labels):
        if not EXPERIMENT_LABEL_RE.fullmatch(label):
            continue  # format errors are already reported by validate_state
        if label not in on_disk:
            errors.append(
                f"objects.experiments: {label} has no experiments/{label}/ directory "
                f"(create it from experiments/_template/ or remove the label)"
            )
    for orphan in sorted(on_disk - labels):
        errors.append(
            f"experiments/{orphan}/ is not listed in objects.experiments "
            f"(add '{orphan}' to research-state.yaml objects.experiments or delete the directory)"
        )


def _check_latest_links(root: Path, errors: list[str]) -> None:
    latest = root / "to_human" / "latest.md"
    try:
        text = latest.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    for target in _MARKDOWN_LINK_RE.findall(text):
        target = target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith("mailto:"):
            continue
        if not (latest.parent / target).resolve().exists() and not (root / target).exists():
            errors.append(
                f"to_human/latest.md: link target '{target}' does not exist "
                f"(fix the path or remove the link)"
            )


def _iter_yaml_payloads(record_path: Path):
    if not record_path.is_file():
        return
    for block in _YAML_BLOCK_RE.findall(record_path.read_text(encoding="utf-8")):
        try:
            payload = yaml.safe_load(block)
        except yaml.YAMLError:
            continue
        if isinstance(payload, dict):
            yield payload


def _check_reference_fields(root: Path, state: dict[str, Any], errors: list[str]) -> None:
    """Decision authorizations and claim evidence must name known objects."""
    objects = state.get("objects") or {}
    known: set[str] = set()
    for values in objects.values():
        if isinstance(values, list):
            known.update(v for v in values if isinstance(v, str))

    for payload in _iter_yaml_payloads(root / "decisions.md"):
        for key in ("experiment_ids", "protocol_refs", "based_on"):
            for ref in payload.get(key) or []:
                if isinstance(ref, str) and _REF_TOKEN_RE.fullmatch(ref) and ref not in known:
                    errors.append(
                        f"decisions.md: {key} references unknown object '{ref}' "
                        f"(add it to research-state.yaml objects or fix the reference)"
                    )

    for payload in _iter_yaml_payloads(root / "claims.md"):
        for key in ("evidence_for", "evidence_against", "hypothesis_refs"):
            for ref in payload.get(key) or []:
                if isinstance(ref, str) and _REF_TOKEN_RE.fullmatch(ref) and ref not in known:
                    errors.append(
                        f"claims.md: {key} references unknown object '{ref}' "
                        f"(add it to research-state.yaml objects or fix the reference)"
                    )


def validate_consistency(project_root: Path) -> list[str]:
    """Check that every indexed object resolves to a file on disk."""
    errors: list[str] = []
    try:
        state = load_state(project_root)
    except FileNotFoundError:
        return [f"{RESEARCH_STATE} missing; fix the base 'rtmpl check' errors first"]
    except ValueError as exc:
        return [str(exc)]
    state_errors = validate_state(state)
    if state_errors:
        # Contract failures block meaningful consistency checks.
        return state_errors
    try:
        policy = load_policy(project_root)
    except FileNotFoundError:
        pass
    except ValueError as exc:
        errors.append(str(exc))
    else:
        errors.extend(validate_policy(policy))

    objects = state.get("objects") or {}
    _check_objects_resolve(project_root, objects, errors)
    _check_experiment_dirs(project_root, objects, errors)
    _check_latest_links(project_root, errors)
    _check_reference_fields(project_root, state, errors)
    return errors

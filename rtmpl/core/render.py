"""Scoped literal placeholder substitution + validation + residual-token check.

Deliberately NOT Jinja — the template carries real ``{{ }}`` in LaTeX
(f-strings, bibtex) that Jinja would corrupt. Substitution is a literal string
replace, scoped per ``render_files``, with regex validation and a post-render
residual-token guard.
"""
from __future__ import annotations

import re

from .hash import is_binary
from .template import TemplateManifest, Variable


class RenderError(Exception):
    pass


def validate_values(manifest: TemplateManifest, values: dict[str, str]) -> dict[str, str]:
    """Validate + default-fill variable values. Returns the resolved values.

    Raises RenderError on: missing required-without-default, validation regex
    failure, or a value that contains a declared token (replacement collision).
    """
    tokens = manifest.all_tokens()
    resolved: dict[str, str] = dict(values)
    for var in manifest.variables:
        val = resolved.get(var.field, "")
        if not val:
            if var.default is not None:
                resolved[var.field] = var.default
                continue
            if var.required:
                raise RenderError(f"required variable {var.field!r} was not provided")
            continue
        if var.validation is not None and not re.fullmatch(var.validation, val):
            raise RenderError(
                f"variable {var.field!r} value {val!r} fails validation {var.validation!r}"
            )
        for tok in tokens:
            if tok and tok in val:
                raise RenderError(
                    f"variable {var.field!r} value {val!r} contains token {tok!r} "
                    "(replacement collision)"
                )
    return resolved


def _vars_for_file(manifest: TemplateManifest, rel_posix: str) -> list[Variable]:
    return [v for v in manifest.variables if rel_posix in v.render_files]


def render_text(content: str, manifest: TemplateManifest, values: dict[str, str], rel_posix: str) -> str:
    result = content
    for var in _vars_for_file(manifest, rel_posix):
        val = values.get(var.field, var.default or "")
        result = result.replace(var.token, val)
    return result


def render_payload(
    payload: dict[str, bytes], manifest: TemplateManifest, values: dict[str, str]
) -> dict[str, bytes]:
    """Render every text file per its render_files; binary files pass through."""
    out: dict[str, bytes] = {}
    for rel, data in payload.items():
        if is_binary(data):
            out[rel] = data
            continue
        out[rel] = render_text(data.decode("utf-8"), manifest, values, rel).encode("utf-8")
    return out


def check_render_residuals(payload: dict[str, bytes], manifest: TemplateManifest) -> None:
    """After render, fail if any declared token remains in a render_file."""
    tokens = manifest.all_tokens()
    for var in manifest.variables:
        for rf in var.render_files:
            data = payload.get(rf)
            if data is None:
                continue
            if is_binary(data):
                raise RenderError(f"render_file {rf!r} is binary; cannot render")
            left = [t for t in tokens if t in data.decode("utf-8")]
            if left:
                raise RenderError(f"residual tokens {left!r} in rendered {rf!r}")

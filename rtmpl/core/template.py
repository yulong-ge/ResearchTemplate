"""Template manifest loading, payload walking, and ``importlib.resources``
location.

The manifest (``template.yaml``) lives in the template source only; downstream
projects never carry it. The walker hard-excludes the manifest itself plus
generated/cache junk so they never leak into a scaffolded project.
"""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

import yaml

_HARDEXCLUDE_DIRS = {"__pycache__"}
_HARDEXCLUDE_NAMES = {"template.yaml", ".DS_Store"}
_HARDEXCLUDE_SUFFIXES = (".pyc", ".pyo")


@dataclass
class Variable:
    token: str
    field: str
    render_files: list[str]
    prompt: str = ""
    required: bool = True
    validation: str | None = None
    default: str | None = None


@dataclass
class TemplateManifest:
    name: str
    display: str
    version: str
    variables: list[Variable] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)

    def variable_for_field(self, field_name: str) -> Variable | None:
        for v in self.variables:
            if v.field == field_name:
                return v
        return None

    def all_tokens(self) -> list[str]:
        return [v.token for v in self.variables]


def templates_root() -> Path:
    """Locate the bundled ``rtmpl/templates`` tree (dev: local; installed: wheel).

    ``RTMPL_TEMPLATES_ROOT`` env var overrides the location (test/dev hook)."""
    import os

    override = os.environ.get("RTMPL_TEMPLATES_ROOT")
    if override:
        return Path(override)
    return Path(str(files("rtmpl") / "templates"))


def list_templates() -> list[str]:
    root = templates_root()
    if not root.exists():
        return []
    return sorted(
        p.name for p in root.iterdir() if p.is_dir() and (p / "template.yaml").exists()
    )


def load_manifest(template_name: str) -> TemplateManifest:
    path = templates_root() / template_name / "template.yaml"
    if not path.exists():
        raise FileNotFoundError(f"template not found: {template_name!r}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    variables = [
        Variable(
            token=vd["token"],
            field=vd["field"],
            render_files=list(vd.get("render_files", []) or []),
            prompt=vd.get("prompt", ""),
            required=vd.get("required", True),
            validation=vd.get("validation"),
            default=vd.get("default"),
        )
        for vd in (data.get("variables") or [])
    ]
    return TemplateManifest(
        name=data["name"],
        display=data.get("display", data["name"]),
        version=str(data["version"]),
        variables=variables,
        exclude=list(data.get("exclude", []) or []),
    )


def _hard_excluded(rel_posix: str) -> bool:
    parts = rel_posix.split("/")
    if any(p in _HARDEXCLUDE_DIRS for p in parts):
        return True
    name = parts[-1]
    if name in _HARDEXCLUDE_NAMES:
        return True
    if name.endswith(_HARDEXCLUDE_SUFFIXES):
        return True
    return False


def _matches_any(rel_posix: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pat) for pat in patterns)


def walk_payload(template_name: str, manifest: TemplateManifest | None = None) -> dict[str, bytes]:
    """Walk the template payload → ``{posix_rel_path: file_bytes}``.

    Hard-excludes the manifest, ``__pycache__``, ``*.pyc``/``*.pyo``,
    ``.DS_Store``, plus the manifest's ``exclude`` globs. Paths are
    POSIX-relative to the template root.
    """
    if manifest is None:
        manifest = load_manifest(template_name)
    root = templates_root() / template_name
    out: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_posix = "/".join(path.relative_to(root).parts)
        if _hard_excluded(rel_posix):
            continue
        if _matches_any(rel_posix, manifest.exclude):
            continue
        out[rel_posix] = path.read_bytes()
    return out

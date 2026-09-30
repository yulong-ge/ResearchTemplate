"""Template manifest loading, payload walking, and ``importlib.resources`` location."""
from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path

import yaml

_HARDEXCLUDE_DIRS = {"__pycache__"}
_HARDEXCLUDE_NAMES = {"template.yaml", ".DS_Store"}
_HARDEXCLUDE_SUFFIXES = (".pyc", ".pyo")
_SUPPORTED_SCHEMA = 1


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
    schema: int = _SUPPORTED_SCHEMA
    variables: list[Variable] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)

    def variable_for_field(self, field_name: str) -> Variable | None:
        for variable in self.variables:
            if variable.field == field_name:
                return variable
        return None

    def all_tokens(self) -> list[str]:
        return [variable.token for variable in self.variables]


def templates_root() -> Path:
    """Locate the bundled ``rtmpl/templates`` tree."""
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
        path.name for path in root.iterdir() if path.is_dir() and (path / "template.yaml").exists()
    )


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"manifest field {field_name!r} must be a non-empty string")
    return value


def _valid_manifest_path(path: str) -> bool:
    if not path or "\\" in path or path.startswith("/"):
        return False
    parts = path.split("/")
    return all(part not in ("", ".", "..", ".rtmpl", ".git") for part in parts)


def _validate_variable(raw: object, index: int, template_root: Path) -> Variable:
    if not isinstance(raw, dict):
        raise ValueError(f"variables[{index}] must be a mapping")
    missing = [key for key in ("token", "field", "render_files") if key not in raw]
    if missing:
        raise ValueError(f"variables[{index}] missing required fields: {', '.join(missing)}")

    token = _require_text(raw["token"], f"variables[{index}].token")
    field_name = _require_text(raw["field"], f"variables[{index}].field")
    render_files = raw["render_files"]
    if not isinstance(render_files, list) or not render_files or not all(
        isinstance(path, str) and _valid_manifest_path(path) for path in render_files
    ):
        raise ValueError(
            f"variables[{index}].render_files must be a non-empty list of safe relative paths"
        )
    missing_files = [path for path in render_files if not (template_root / path).is_file()]
    if missing_files:
        raise ValueError(
            f"variables[{index}].render_files reference missing files: {', '.join(missing_files)}"
        )

    prompt = raw.get("prompt", "")
    if not isinstance(prompt, str):
        raise ValueError(f"variables[{index}].prompt must be a string")
    required = raw.get("required", True)
    if not isinstance(required, bool):
        raise ValueError(f"variables[{index}].required must be a boolean")
    validation = raw.get("validation")
    if validation is not None and not isinstance(validation, str):
        raise ValueError(f"variables[{index}].validation must be a string or null")
    default = raw.get("default")
    if default is not None and not isinstance(default, str):
        raise ValueError(f"variables[{index}].default must be a string or null")

    return Variable(
        token=token,
        field=field_name,
        render_files=list(render_files),
        prompt=prompt,
        required=required,
        validation=validation,
        default=default,
    )


def load_manifest(template_name: str) -> TemplateManifest:
    if (
        not isinstance(template_name, str)
        or not template_name
        or "\\" in template_name
        or Path(template_name).name != template_name
        or template_name in {".", ".."}
    ):
        raise ValueError(f"unsafe template name: {template_name!r}")
    template_root = templates_root() / template_name
    path = template_root / "template.yaml"
    if not path.exists():
        raise FileNotFoundError(f"template not found: {template_name!r}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("manifest root must be a mapping")

    removed_keys = sorted({"file_policies", "init_guidance"} & set(data))
    if removed_keys:
        raise ValueError("manifest contains removed research fields: " + ", ".join(removed_keys))

    schema = data.get("schema", _SUPPORTED_SCHEMA)
    if isinstance(schema, bool) or not isinstance(schema, int) or schema != _SUPPORTED_SCHEMA:
        raise ValueError(f"unsupported manifest schema: {schema!r}")
    name = _require_text(data.get("name"), "name")
    if name != template_name:
        raise ValueError(f"manifest name {name!r} does not match template directory {template_name!r}")
    display = data.get("display", name)
    if not isinstance(display, str) or not display.strip():
        raise ValueError("manifest field 'display' must be a non-empty string")
    version = _require_text(data.get("version"), "version")

    raw_exclude = data.get("exclude", []) or []
    if not isinstance(raw_exclude, list) or not all(isinstance(pattern, str) for pattern in raw_exclude):
        raise ValueError("exclude must be a list of path globs")
    for pattern in raw_exclude:
        if not _valid_exclude_pattern(pattern):
            raise ValueError(f"unsafe exclude pattern: {pattern!r}")

    raw_variables = data.get("variables", []) or []
    if not isinstance(raw_variables, list):
        raise ValueError("variables must be a list")
    variables = [_validate_variable(raw, index, template_root) for index, raw in enumerate(raw_variables)]
    fields = [variable.field for variable in variables]
    tokens = [variable.token for variable in variables]
    if len(fields) != len(set(fields)):
        raise ValueError("variables contain duplicate field names")
    if len(tokens) != len(set(tokens)):
        raise ValueError("variables contain duplicate tokens")

    return TemplateManifest(
        name=name,
        display=display,
        version=version,
        schema=schema,
        variables=variables,
        exclude=list(raw_exclude),
    )


def _hard_excluded(rel_posix: str) -> bool:
    parts = rel_posix.split("/")
    if any(part in _HARDEXCLUDE_DIRS for part in parts):
        return True
    name = parts[-1]
    return name in _HARDEXCLUDE_NAMES or name.endswith(_HARDEXCLUDE_SUFFIXES)


def _matches_any(rel_posix: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel_posix, pattern) for pattern in patterns)


def _valid_exclude_pattern(pattern: str) -> bool:
    """Accept relative POSIX globs without traversal or metadata escapes."""
    if not pattern or "\\" in pattern or pattern.startswith("/"):
        return False
    return all(segment not in ("", ".", "..", ".rtmpl", ".git") for segment in pattern.split("/"))


def walk_payload(template_name: str, manifest: TemplateManifest | None = None) -> dict[str, bytes]:
    """Walk the template payload to ``{posix_rel_path: file_bytes}``."""
    if manifest is None:
        manifest = load_manifest(template_name)
    root = templates_root() / template_name
    out: dict[str, bytes] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_posix = "/".join(path.relative_to(root).parts)
        if _hard_excluded(rel_posix) or _matches_any(rel_posix, manifest.exclude):
            continue
        out[rel_posix] = path.read_bytes()
    return out

"""Unit tests for core modules: hash, state, classify, version, render."""
from __future__ import annotations

import json

import pytest

from rtmpl.core import classify, hash as h, render, state, version
from rtmpl.core.backup import create_backup
from rtmpl.core.template import TemplateManifest, Variable

A = classify.ABSENT


# --- hash -------------------------------------------------------------------

def test_hash_text_crlf_normalization():
    assert h.hash_text("a\r\nb") == h.hash_text("a\nb")


def test_hash_binary_detection_and_raw():
    data = b"\x00pdf\x00"
    assert h.is_binary(data)
    assert not h.is_binary(b"plain text")
    assert h.hash_bytes(data) == h.hash_bytes(data)


def test_hash_data_dispatch():
    assert h.hash_data(b"hello") == h.hash_text("hello")
    assert h.hash_data(b"\x00x") == h.hash_bytes(b"\x00x")


# --- state ------------------------------------------------------------------

def test_state_path_key_validation():
    assert state.is_valid_path_key("src/paths.py")
    assert state.is_valid_path_key("a/b/c.md")
    for bad in ("../etc", "/abs", ".rtmpl/x", ".git/config", "a\\b", "", ".", "..", "a//b"):
        assert not state.is_valid_path_key(bad), bad


def test_state_load_statuses(tmp_path):
    rd = tmp_path / ".rtmpl"
    assert state.load_state(rd)[1] == "missing"

    rd.mkdir()
    (rd / "state.json").write_text("{not json")
    assert state.load_state(rd)[1] == "corrupt"

    (rd / "state.json").write_text(json.dumps({"schema": 1, "template_version": "1", "hashes": {}}))
    assert state.load_state(rd)[1] == "unsupported"

    (rd / "state.json").write_text(json.dumps({"schema": 2, "hashes": {}}))
    assert state.load_state(rd)[1] == "version_unknown"

    (rd / "state.json").write_text(
        json.dumps({"schema": 2, "template_version": "1.0", "hashes": {"../x": "h"}})
    )
    assert state.load_state(rd)[1] == "corrupt"  # unsafe key

    (rd / "state.json").write_text(
        json.dumps({"schema": 2, "template_version": "1.0", "hashes": {"a": "h", "b": None}})
    )
    s, st = state.load_state(rd)
    assert st == "ok" and s.template_version == "1.0" and s.hashes["b"] is None

    (rd / "state.json").write_text(
        json.dumps(
            {
                "schema": 2,
                "template_version": "1.0",
                "hashes": {"a": "h"},
                "ownership": {"research-state.yaml": "seed_only"},
            }
        )
    )
    legacy, legacy_status = state.load_state(rd)
    assert legacy_status == "ok"
    assert legacy.hashes == {"a": "h"}


def test_state_atomic_save_roundtrip(tmp_path):
    rd = tmp_path / ".rtmpl"
    state.save_state(rd, state.State(template_version="2.0", hashes={"a": "x", "d": None}))
    s, st = state.load_state(rd)
    assert st == "ok" and s.hashes == {"a": "x", "d": None}
    raw = json.loads((rd / "state.json").read_text(encoding="utf-8"))
    assert "ownership" not in raw


def test_backup_names_do_not_collide(tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    (project / "a.txt").write_text("a\n")
    rd = project / ".rtmpl"
    first = create_backup(rd, project, ["a.txt"])
    second = create_backup(rd, project, ["a.txt"])
    assert first != second
    assert first.exists() and second.exists()


# --- classify (total, 8 rows) -----------------------------------------------

def test_classify_all_rows():
    assert classify.classify_path(True, True, True, "h", "h") == "unchanged"
    assert classify.classify_path(True, True, False, "diskh", "diskh") == "autoUpdate"
    assert classify.classify_path(True, True, False, "other", "diskh") == "changed"
    assert classify.classify_path(True, True, False, None, "diskh") == "changed"  # tombstone, disk!=tmpl
    assert classify.classify_path(True, True, False, A, "diskh") == "changed"  # untracked, disk!=tmpl
    assert classify.classify_path(True, False, False, A, None) == "new"
    assert classify.classify_path(True, False, False, "h", None) == "userDeleted"
    assert classify.classify_path(True, False, False, None, None) == "userDeleted"  # tombstone kept
    assert classify.classify_path(False, True, False, "diskh", "diskh") == "orphanedPristine"
    assert classify.classify_path(False, True, False, "other", "diskh") == "orphanedModified"
    assert classify.classify_path(False, True, False, None, "diskh") == "orphanedModified"
    assert classify.classify_path(False, False, False, "h", None) == "deadOrphan"
    assert classify.classify_path(False, False, False, None, None) == "deadOrphan"


# --- version ----------------------------------------------------------------

def test_version_skew():
    assert version.compare("0.2.0", "0.1.0") == "forward"
    assert version.compare("0.1.0", "0.1.0") == "equal"
    assert version.compare("0.1.0", "0.2.0") == "downgrade"


# --- render -----------------------------------------------------------------

def _manifest():
    return TemplateManifest(
        name="d",
        display="d",
        version="1",
        variables=[Variable(token="<proj>", field="proj", render_files=["a.txt"], validation="^[a-z]+$")],
    )


def test_render_validate_ok():
    assert render.validate_values(_manifest(), {"proj": "ab"})["proj"] == "ab"


def test_render_validate_failures():
    m = _manifest()
    with pytest.raises(render.RenderError):
        render.validate_values(m, {"proj": "AB"})  # regex
    with pytest.raises(render.RenderError):
        render.validate_values(m, {})  # required missing
    with pytest.raises(render.RenderError):
        render.validate_values(m, {"proj": "<proj>"})  # collision (also fails regex)


def test_render_scoped_substitution():
    m = _manifest()
    out = render.render_payload({"a.txt": b"name=<proj>", "b.txt": b"<proj>"}, m, {"proj": "ab"})
    assert out["a.txt"] == b"name=ab"
    assert out["b.txt"] == b"<proj>"  # not a render_file → untouched


def test_render_residual_check():
    m = TemplateManifest(
        name="d", display="d", version="1",
        variables=[Variable(token="<proj>", field="proj", render_files=["a.txt"])],
    )
    payload = render.render_payload({"a.txt": b"name=<proj>"}, m, {"proj": "ab"})
    # No residual after a complete render → check passes (no raise).
    render.check_render_residuals(payload, m)
    assert payload["a.txt"] == b"name=ab"


def test_manifest_excludes_paths(tmp_path, monkeypatch):
    root = tmp_path / "templates" / "demo"
    root.mkdir(parents=True)
    (root / "template.yaml").write_text(
        "schema: 1\nname: demo\nversion: '1'\nexclude: ['research/_generated/**']\n"
    )
    (root / "research").mkdir()
    (root / "research" / "ideas.md").write_text("ideas")
    (root / "research" / "_generated").mkdir()
    (root / "research" / "_generated" / "graph.json").write_text("{}")
    monkeypatch.setenv("RTMPL_TEMPLATES_ROOT", str(tmp_path / "templates"))
    from rtmpl.core.template import load_manifest, walk_payload

    manifest = load_manifest("demo")
    assert not hasattr(manifest, "policy_for")
    assert "research/ideas.md" in walk_payload("demo", manifest)
    assert "research/_generated/graph.json" not in walk_payload("demo", manifest)


def test_manifest_rejects_removed_research_fields(tmp_path, monkeypatch):
    root = tmp_path / "templates" / "demo"
    root.mkdir(parents=True)
    (root / "template.yaml").write_text(
        "schema: 1\nname: demo\nversion: '1'\nfile_policies: {}\n"
    )
    monkeypatch.setenv("RTMPL_TEMPLATES_ROOT", str(tmp_path / "templates"))
    from rtmpl.core.template import load_manifest

    with pytest.raises(ValueError, match="removed research fields"):
        load_manifest("demo")


def test_manifest_rejects_non_mapping(tmp_path, monkeypatch):
    root = tmp_path / "templates" / "demo"
    root.mkdir(parents=True)
    (root / "template.yaml").write_text("- demo\n")
    monkeypatch.setenv("RTMPL_TEMPLATES_ROOT", str(tmp_path / "templates"))
    from rtmpl.core.template import load_manifest

    with pytest.raises(ValueError, match="root must be a mapping"):
        load_manifest("demo")


def test_manifest_rejects_missing_render_file(tmp_path, monkeypatch):
    root = tmp_path / "templates" / "demo"
    root.mkdir(parents=True)
    (root / "template.yaml").write_text(
        "schema: 1\nname: demo\nversion: '1'\n"
        "variables: [{token: '<x>', field: x, render_files: ['missing.txt']}]\n"
    )
    monkeypatch.setenv("RTMPL_TEMPLATES_ROOT", str(tmp_path / "templates"))
    from rtmpl.core.template import load_manifest

    with pytest.raises(ValueError, match="missing files"):
        load_manifest("demo")


def test_manifest_rejects_duplicate_variable_fields(tmp_path, monkeypatch):
    root = tmp_path / "templates" / "demo"
    root.mkdir(parents=True)
    (root / "a.txt").write_text("<a>")
    (root / "b.txt").write_text("<b>")
    (root / "template.yaml").write_text(
        "schema: 1\nname: demo\nversion: '1'\n"
        "variables: [{token: '<a>', field: x, render_files: ['a.txt']}, "
        "{token: '<b>', field: x, render_files: ['b.txt']}]\n"
    )
    monkeypatch.setenv("RTMPL_TEMPLATES_ROOT", str(tmp_path / "templates"))
    from rtmpl.core.template import load_manifest

    with pytest.raises(ValueError, match="duplicate field"):
        load_manifest("demo")

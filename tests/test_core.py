"""Unit tests for core modules: hash, state, classify, version, render."""
from __future__ import annotations

import json

import pytest

from rtmpl.core import classify, hash as h, render, state, version
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


def test_state_atomic_save_roundtrip(tmp_path):
    rd = tmp_path / ".rtmpl"
    state.save_state(rd, state.State(template_version="2.0", hashes={"a": "x", "d": None}))
    s, st = state.load_state(rd)
    assert st == "ok" and s.hashes == {"a": "x", "d": None}


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

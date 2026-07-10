"""End-to-end command tests against a disposable mini template (plan §13)."""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import shutil

import pytest

from rtmpl.commands import adopt, new, repair, update
from rtmpl.commands._common import CommandError
from rtmpl.commands.update import _write_new
from rtmpl.core import hash as h
from rtmpl.core.render import RenderError
from rtmpl.core.state import load_state, save_state


def _a(**kw):
    base = dict(
        force=False, skip=False, dry_run=False, no_input=True, allow_downgrade=False,
        template=None, var={}, name=None, path=None, repair=False,
    )
    base.update(kw)
    return argparse.Namespace(**base)


def _new(proj, **kw):
    return new.run(_a(name="ab", template="demo", path=str(proj), **kw))


def _update(proj, monkeypatch, **kw):
    monkeypatch.chdir(proj)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = update.run(_a(**kw))
    return rc, buf.getvalue()


# --- new --------------------------------------------------------------------

def test_new_renders_and_state(mini_template, tmp_path):
    proj = tmp_path / "p"
    assert _new(proj) == 0
    assert (proj / "pyproject.toml").read_text() == 'name = "ab"\n'
    assert not (proj / "template.yaml").exists()  # manifest not downstream
    s, st = load_state(proj / ".rtmpl")
    assert st == "ok" and s.template_version == "0.1.0"
    assert "AGENTS.md" in s.hashes and "binary.pdf" in s.hashes


def test_new_nonempty_target_error(mini_template, tmp_path):
    proj = tmp_path / "p"
    proj.mkdir()
    (proj / "x").write_text("y")
    with pytest.raises(CommandError):
        _new(proj)


def test_new_bad_var_rejected(mini_template, tmp_path):
    with pytest.raises(RenderError):
        new.run(_a(name="AB", template="demo", path=str(tmp_path / "p")))


def test_new_binary_tracked_raw(mini_template, tmp_path):
    proj = tmp_path / "p"
    _new(proj)
    raw = (mini_template / "binary.pdf").read_bytes()
    s, _ = load_state(proj / ".rtmpl")
    assert s.hashes["binary.pdf"] == h.hash_bytes(raw)  # raw hash
    assert (proj / "binary.pdf").read_bytes() == raw  # byte-exact


# --- adopt ------------------------------------------------------------------

def test_adopt_customized_is_changed_not_clobber(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / "AGENTS.md").write_text("# customized\n")
    shutil.rmtree(proj / ".rtmpl")  # simulate legacy cp (no rtmpl state)
    monkeypatch.chdir(proj)
    adopt.run(_a(template="demo", var={"proj": "ab"}))
    s, st = load_state(proj / ".rtmpl")
    assert st == "ok"
    # baseline = TEMPLATE hash, so a customized file is 'changed' (never auto-clobber)
    assert s.hashes["AGENTS.md"] == h.hash_text("# agents\n")
    _, out = _update(proj, monkeypatch, dry_run=True)
    assert "? AGENTS.md" in out


def test_adopt_missing_is_new(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / "AGENTS.md").unlink()
    shutil.rmtree(proj / ".rtmpl")
    monkeypatch.chdir(proj)
    adopt.run(_a(template="demo", var={"proj": "ab"}))
    s, _ = load_state(proj / ".rtmpl")
    assert "AGENTS.md" not in s.hashes  # omitted → first update adds it
    _update(proj, monkeypatch)  # new → auto-write, no prompt
    assert (proj / "AGENTS.md").exists()


# --- update: autoupdate / orphan / changed ---------------------------------

def test_update_autoupdate(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (mini_template / "AGENTS.md").write_text("# new agents\n")
    _update(proj, monkeypatch)  # autoUpdate, no prompt
    assert (proj / "AGENTS.md").read_text() == "# new agents\n"


def test_orphan_safe_delete(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (mini_template / "AGENTS.md").unlink()  # removed from template
    assert (proj / "AGENTS.md").exists()
    _update(proj, monkeypatch, force=True)  # orphanedPristine → delete
    assert not (proj / "AGENTS.md").exists()


def test_changed_force_overwrite(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / "AGENTS.md").write_text("# customized\n")
    (mini_template / "AGENTS.md").write_text("# new agents\n")
    _update(proj, monkeypatch, force=True)
    assert (proj / "AGENTS.md").read_text() == "# new agents\n"


# --- tombstone lifecycle ----------------------------------------------------

def test_userdeleted_then_return_clears_tombstone(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / "AGENTS.md").unlink()
    _update(proj, monkeypatch)  # userDeleted → tombstone
    s, _ = load_state(proj / ".rtmpl")
    assert s.hashes["AGENTS.md"] is None
    (proj / "AGENTS.md").write_text("# agents\n")  # restore == template
    _update(proj, monkeypatch)  # unchanged + state-heal clears tombstone
    s, _ = load_state(proj / ".rtmpl")
    assert s.hashes["AGENTS.md"] == h.hash_text("# agents\n")


# --- repair -----------------------------------------------------------------

def test_repair_tombstones_missing_no_recreate(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / "AGENTS.md").unlink()
    (proj / ".rtmpl" / "state.json").write_text("{corrupt")
    monkeypatch.chdir(proj)
    repair.run(_a(template="demo"))
    s, st = load_state(proj / ".rtmpl")
    assert st == "ok"
    assert s.hashes.get("AGENTS.md") is None  # tombstone (repair semantics)
    _update(proj, monkeypatch)
    assert not (proj / "AGENTS.md").exists()  # not recreated


# --- skew / path-key / create-new collision --------------------------------

def test_equal_version_still_classifies(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / "AGENTS.md").write_text("# customized\n")
    _, out = _update(proj, monkeypatch, dry_run=True)
    assert "? AGENTS.md" in out  # not a no-op at equal version


def test_skew_downgrade_aborts(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    s, _ = load_state(proj / ".rtmpl")
    s.template_version = "0.2.0"
    save_state(proj / ".rtmpl", s)
    with pytest.raises(CommandError):
        _update(proj, monkeypatch, allow_downgrade=False)


def test_path_key_injection_is_corrupt(tmp_path):
    rd = tmp_path / ".rtmpl"
    rd.mkdir()
    (rd / "state.json").write_text(
        json.dumps({"schema": 2, "template_version": "1", "hashes": {"../evil": "h"}})
    )
    _, st = load_state(rd)
    assert st == "corrupt"


def test_write_new_collision_preserves(tmp_path):
    f = tmp_path / "f.txt"
    _write_new(f, b"v1")
    assert (tmp_path / "f.txt.new").read_bytes() == b"v1"
    _write_new(f, b"v2")
    assert (tmp_path / "f.txt.new.1").read_bytes() == b"v2"
    assert (tmp_path / "f.txt.new").read_bytes() == b"v1"  # leftover preserved


def test_interrupt_aborts(mini_template, tmp_path, monkeypatch):
    proj = tmp_path / "p"
    _new(proj)
    (proj / ".rtmpl" / ".pending").write_text("interrupted")
    with pytest.raises(CommandError):
        _update(proj, monkeypatch)

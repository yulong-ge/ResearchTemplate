from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from rtmpl.commands import check, resume
from rtmpl.commands._common import CommandError


TEMPLATE = Path(__file__).parents[1] / "rtmpl" / "templates" / "batchcom-research"


def _project(tmp_path: Path) -> Path:
    for rel in (
        "research-state.yaml",
        "hypotheses.md",
        "research-log.md",
        "findings.md",
        "claims.md",
        "decisions.md",
        "research/policy.yaml",
        "to_human/latest.md",
        "to_human/evolution.mmd",
        "to_human/evidence.mmd",
        "to_human/trajectory.csv",
    ):
        source = TEMPLATE / rel
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    return tmp_path


def test_check_accepts_template_contract(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert check.run(object()) == 0
    assert capsys.readouterr().out.strip() == "Research contract: OK"


def test_check_reports_dangling_relationship(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    state.write_text(
        state.read_text(encoding="utf-8").replace(
            "relations: []",
            "objects:\n  hypotheses: [H1]\n  experiments: []\n  results: []\n  findings: []\n  claims: []\n  decisions: []\nrelations:\n  - {from: H1, to: E1, type: tested_by}\n",
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="unknown to ID"):
        check.run(object())


def test_resume_prints_state_header_and_human_brief(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert resume.run(object()) == 0
    output = capsys.readouterr().out
    assert "Status: candidate" in output
    assert "Loop: inner=auto outer=human" in output
    assert "# Current research" in output


def test_check_rejects_invalid_policy_loop_mode(tmp_path, monkeypatch):
    project = _project(tmp_path)
    policy = project / "research" / "policy.yaml"
    policy.write_text(
        policy.read_text(encoding="utf-8").replace("outer: human", "outer: interactive"),
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="loop_control.outer"):
        check.run(object())

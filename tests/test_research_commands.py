from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

from rtmpl.commands import check, doctor, graph, pause, resume, summary
from rtmpl.commands._common import CommandError


TEMPLATE = Path(__file__).parents[1] / "rtmpl" / "templates" / "batchcom-research"


def _project(tmp_path: Path) -> Path:
    for rel in (
        "hypotheses.md",
        "research-log.md",
        "findings.md",
        "claims.md",
        "decisions.md",
        "to_human/latest.md",
        "to_human/evolution.mmd",
        "to_human/evidence.mmd",
        "to_human/trajectory.csv",
    ):
        source = TEMPLATE / rel
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
    # Write the automation_mode contract explicitly so the fixture is stable
    # whether or not the template records have been migrated yet.
    state = {
        "schema_version": 1,
        "research_question": "Does X improve Y under Z?",
        "status": "candidate",
        "active_direction": None,
        "active_hypothesis": None,
        "automation_mode": "inherit_policy",
        "next_action": {
            "owner": "agent",
            "text": "run the first probe",
            "done_when": "probe result recorded",
        },
        "waiting": {"reason": None, "on": None, "unblock_action": None},
        "objects": {
            "hypotheses": [],
            "experiments": [],
            "results": [],
            "findings": [],
            "claims": [],
            "decisions": [],
        },
        "relations": [],
    }
    (tmp_path / "research-state.yaml").write_text(
        yaml.safe_dump(state, sort_keys=False), encoding="utf-8"
    )
    policy = yaml.safe_load(
        (TEMPLATE / "research" / "policy.yaml").read_text(encoding="utf-8")
    )
    policy.pop("loop_control", None)
    policy["automation_mode"] = "semi-auto"
    target = tmp_path / "research" / "policy.yaml"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(yaml.safe_dump(policy, sort_keys=False), encoding="utf-8")
    return tmp_path


def _args(**kw):
    return argparse.Namespace(**kw)


def test_check_accepts_template_contract(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert check.run(_args(consistency=False)) == 0
    assert capsys.readouterr().out.strip() == "Research contract: OK"


def test_check_reports_dangling_relationship(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    payload = yaml.safe_load(state.read_text(encoding="utf-8"))
    payload["objects"]["hypotheses"] = ["H1"]
    payload["relations"] = [{"from": "H1", "to": "E1", "type": "tested_by"}]
    state.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="unknown to ID"):
        check.run(_args(consistency=False))


def test_check_rejects_invalid_experiment_label(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    payload = yaml.safe_load(state.read_text(encoding="utf-8"))
    payload["objects"]["experiments"] = ["E1"]  # old prefix form is now invalid
    state.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="invalid ID"):
        check.run(_args(consistency=False))


def test_check_accepts_semantic_experiment_label(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    payload = yaml.safe_load(state.read_text(encoding="utf-8"))
    payload["objects"]["experiments"] = ["batch-size-01"]
    state.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    monkeypatch.chdir(project)

    assert check.run(_args(consistency=False)) == 0


def test_resume_prints_state_header_and_human_brief(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert resume.run(_args()) == 0
    output = capsys.readouterr().out
    assert "Status: candidate" in output
    assert "Automation: semi-auto" in output
    assert "# Current research" in output


def test_check_rejects_invalid_policy_automation_mode(tmp_path, monkeypatch):
    project = _project(tmp_path)
    policy = project / "research" / "policy.yaml"
    payload = yaml.safe_load(policy.read_text(encoding="utf-8"))
    payload["automation_mode"] = "interactive"
    policy.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="automation_mode"):
        check.run(_args(consistency=False))


def test_consistency_catches_dangling_experiment_label(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    payload = yaml.safe_load(state.read_text(encoding="utf-8"))
    payload["objects"]["experiments"] = ["batch-size-01"]
    state.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="no experiments/batch-size-01"):
        check.run(_args(consistency=True))


def test_consistency_catches_orphan_experiment_dir(tmp_path, monkeypatch):
    project = _project(tmp_path)
    orphan = project / "experiments" / "lr-schedule-02"
    orphan.mkdir(parents=True)
    (orphan / "protocol.md").write_text("# protocol\n", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="lr-schedule-02.*not listed"):
        check.run(_args(consistency=True))


def test_consistency_passes_with_declared_objects(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    payload = yaml.safe_load(state.read_text(encoding="utf-8"))
    payload["objects"]["hypotheses"] = ["H1"]
    payload["objects"]["experiments"] = ["batch-size-01"]
    payload["objects"]["results"] = ["R1"]
    payload["relations"] = [
        {"from": "H1", "to": "batch-size-01", "type": "tested_by"},
        {"from": "batch-size-01", "to": "R1", "type": "produced"},
    ]
    state.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    (project / "hypotheses.md").write_text(
        "## H1: title\n\n```yaml\nid: H1\n```\n", encoding="utf-8"
    )
    exp = project / "experiments" / "batch-size-01"
    exp.mkdir(parents=True)
    (exp / "result.md").write_text(
        "```yaml\nid: R1\nexperiment_id: batch-size-01\n```\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    assert check.run(_args(consistency=True)) == 0


def test_consistency_catches_broken_latest_link(tmp_path, monkeypatch):
    project = _project(tmp_path)
    latest = project / "to_human" / "latest.md"
    latest.write_text(
        latest.read_text(encoding="utf-8") + "\n[ghost](missing-file.md)\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="missing-file.md"):
        check.run(_args(consistency=True))


def test_pause_writes_paused_context(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert pause.run(_args()) == 0
    out = project / "to_human" / "paused-context.md"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "Paused at:" in text
    assert "run the first probe" in text
    assert "Open notes" in text
    assert "paused-context.md" in capsys.readouterr().out


def test_pause_requires_valid_state(tmp_path, monkeypatch):
    project = _project(tmp_path)
    (project / "research-state.yaml").write_text("not: [valid", encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="cannot pause"):
        pause.run(_args())


def test_resume_prints_paused_context_first(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)
    pause.run(_args())
    capsys.readouterr()

    assert resume.run(_args()) == 0
    output = capsys.readouterr().out
    paused_idx = output.index("Paused at:")
    status_idx = output.index("Status: candidate")
    assert paused_idx < status_idx


def test_doctor_passes_on_filled_project(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert doctor.run(_args()) == 0
    assert "all checks pass" in capsys.readouterr().out


def test_doctor_fails_on_unfilled_template(tmp_path, monkeypatch):
    project = _project(tmp_path)
    state = project / "research-state.yaml"
    payload = yaml.safe_load(state.read_text(encoding="utf-8"))
    payload["research_question"] = "<one-line research question>"
    payload["next_action"]["text"] = "<one concrete next action>"
    state.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="placeholder"):
        doctor.run(_args())


def test_summary_requires_builder(tmp_path, monkeypatch):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="dashboard_builder"):
        summary.run(_args(open=False))


def test_dashboard_builder_produces_html(tmp_path):
    project = _project(tmp_path)
    src = project / "src"
    src.mkdir(exist_ok=True)
    shutil.copyfile(
        TEMPLATE / "src" / "dashboard_builder.py", src / "dashboard_builder.py"
    )
    result = subprocess.run(
        [sys.executable, "src/dashboard_builder.py"],
        cwd=project,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    dashboard = project / "to_human" / "dashboard.html"
    assert dashboard.is_file()
    html = dashboard.read_text(encoding="utf-8")
    assert "Does X improve Y under Z?" in html
    assert "semi-auto" in html
    assert "<!DOCTYPE html>" in html


def test_graph_prints_evolution_mmd(tmp_path, monkeypatch, capsys):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    assert graph.run(_args(render=None)) == 0
    out = capsys.readouterr().out
    assert "flowchart" in out
    assert "tested_by" in out


def test_graph_rejects_non_image_extension(tmp_path, monkeypatch):
    project = _project(tmp_path)
    monkeypatch.chdir(project)

    with pytest.raises(CommandError, match="png"):
        graph.run(_args(render="out.txt"))


def test_graph_missing_evolution_errors(tmp_path, monkeypatch):
    tmp_path.joinpath("to_human").mkdir()
    monkeypatch.chdir(tmp_path)

    with pytest.raises(CommandError, match="evolution.mmd"):
        graph.run(_args(render=None))

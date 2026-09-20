"""Structural tests for research-record ownership in generated projects."""
from pathlib import Path

from rtmpl.core.template import load_manifest


TEMPLATE = (
    Path(__file__).parents[1]
    / "rtmpl"
    / "templates"
    / "batchcom-research"
)


def test_template_owns_experiments_but_not_per_run_git_records():
    assert (TEMPLATE / "experiments" / "README.md").is_file()
    assert not (TEMPLATE / "research" / "runs").exists()

    policy = "\n".join(
        (TEMPLATE / name).read_text(encoding="utf-8")
        for name in ("AGENTS.md", "README.md")
    )
    assert "experiments/<id>/" in policy
    assert "run-level state" in policy
    assert "Operational heartbeats and routine health checks stay in machine logs" in policy


def test_template_does_not_copy_global_skills():
    assert not (TEMPLATE / ".agents" / "skills").exists()


def test_v04_record_and_experiment_skeletons_exist():
    for path in (
        TEMPLATE / "docs" / "research-workflow.md",
        TEMPLATE / "docs" / "manual-migration.md",
        TEMPLATE / "research-state.yaml",
        TEMPLATE / "hypotheses.md",
        TEMPLATE / "research-log.md",
        TEMPLATE / "findings.md",
        TEMPLATE / "claims.md",
        TEMPLATE / "decisions.md",
        TEMPLATE / "to_human" / "latest.md",
        TEMPLATE / "to_human" / "evolution.mmd",
        TEMPLATE / "to_human" / "evidence.mmd",
        TEMPLATE / "to_human" / "trajectory.csv",
        TEMPLATE / "research" / "policy.yaml",
        TEMPLATE / "experiments" / "_template" / "protocol.md",
        TEMPLATE / "experiments" / "_template" / "result.md",
        TEMPLATE / "experiments" / "_template" / "analysis.md",
    ):
        assert path.is_file(), path
    manifest = (TEMPLATE / "template.yaml").read_text(encoding="utf-8")
    assert "seed_only:" in manifest and "research-state.yaml" in manifest

    loaded = load_manifest("batchcom-research")
    assert [step.path for step in loaded.init_guidance][:2] == [
        "research-state.yaml",
        "to_human/latest.md",
    ]
    assert loaded.policy_for("literature/survey.md") == "seed_only"
    assert loaded.policy_for("paper/README.md") == "managed"


def test_obsolete_overview_paths_are_removed_from_the_template():
    for path in (
        TEMPLATE / "research" / "overview.md",
        TEMPLATE / "research" / "ideas.md",
        TEMPLATE / "research" / "findings.md",
        TEMPLATE / "research" / "claims.md",
        TEMPLATE / "research" / "decisions.md",
        TEMPLATE / "research" / "log.md",
    ):
        assert not path.exists(), path

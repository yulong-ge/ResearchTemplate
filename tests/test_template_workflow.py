"""Structural tests for the human-guided copyable workspace."""
from pathlib import Path

from rtmpl.core.template import load_manifest, walk_payload


TEMPLATE = Path(__file__).parents[1] / "rtmpl" / "templates" / "batchcom-research"


def test_template_contains_the_minimal_human_workflow():
    for path in (
        TEMPLATE / "AGENTS.md",
        TEMPLATE / "README.md",
        TEMPLATE / "docs" / "plans" / "README.md",
        TEMPLATE / "experiments" / "README.md",
        TEMPLATE / "notes" / "README.md",
        TEMPLATE / "notes" / "environment.md",
        TEMPLATE / "notes" / "templates" / "plan.md",
        TEMPLATE / "notes" / "templates" / "daily.md",
        TEMPLATE / "notes" / "templates" / "weekly.md",
        TEMPLATE / "notes" / "templates" / "review.md",
        TEMPLATE / "notes" / "daily" / ".gitkeep",
        TEMPLATE / "notes" / "weekly" / ".gitkeep",
        TEMPLATE / "literature" / "notes" / ".gitkeep",
        TEMPLATE / "paper" / "README.md",
    ):
        assert path.is_file(), path

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            TEMPLATE / "AGENTS.md",
            TEMPLATE / "README.md",
            TEMPLATE / "docs" / "plans" / "README.md",
            TEMPLATE / "experiments" / "README.md",
            TEMPLATE / "notes" / "README.md",
        )
    )
    assert "Plan" in text
    assert "experiments/" in text
    assert "日报" in text and "周报" in text
    assert "可改" in text
    for stale in (
        "research-state.yaml",
        "automation_mode",
        "research-record",
        "hypothesis ledger",
        "protocol bundle",
        "post-run Markdown",
    ):
        assert stale not in text


def test_template_removes_research_ledger_and_fixed_experiment_schema():
    removed = (
        "research-state.yaml",
        "hypotheses.md",
        "findings.md",
        "claims.md",
        "decisions.md",
        "research-log.md",
        "research",
        "to_human",
        "experiments/_template",
        "src/dashboard_builder.py",
        "docs/research-workflow.md",
        "docs/manual-migration.md",
        "literature/survey.md",
        "docs/human-note-organization.md",
    )
    for rel in removed:
        assert not (TEMPLATE / rel).exists(), rel


def test_template_manifest_has_no_research_semantics():
    manifest_text = (TEMPLATE / "template.yaml").read_text(encoding="utf-8")
    for token in ("seed_only", "generated", "file_policies", "init_guidance"):
        assert token not in manifest_text

    manifest = load_manifest("batchcom-research")
    assert manifest.schema == 1
    assert manifest.version == "0.7.0"
    assert not hasattr(manifest, "policy_for")
    payload = walk_payload("batchcom-research", manifest)
    assert "notes/README.md" in payload
    assert "experiments/README.md" in payload
    assert "notes/templates/plan.md" in payload


def test_template_does_not_copy_global_skills():
    assert not (TEMPLATE / ".agents" / "skills").exists()


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


def test_plan_template_keeps_one_experiment_in_one_file():
    plan = (TEMPLATE / "notes" / "templates" / "plan.md").read_text(encoding="utf-8")
    for section in ("## 问题", "## 做法", "## 给 Agent 的范围", "## 结果", "## 结论与下一步"):
        assert section in plan
    for stale in ("E-0", "H-0", "D-0", "protocol.md", "result.md"):
        assert stale not in plan

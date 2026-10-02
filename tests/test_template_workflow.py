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
    assert "可以改哪些路径" in text
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


def test_agents_md_describes_the_project_not_the_template():
    agents = (TEMPLATE / "AGENTS.md").read_text(encoding="utf-8")
    assert agents.startswith("# <proj>")
    assert "## 研究项目" in agents
    assert "研究问题" in agents and "评价指标" in agents
    manifest = load_manifest("batchcom-research")
    for var in manifest.variables:
        assert "AGENTS.md" in var.render_files


def test_batchcom_and_terminal_rules_live_only_in_global_skills():
    for rel in ("AGENTS.md", "notes/environment.md", ".opencode/agents/remote-exec.md", "src/paths.py"):
        text = (TEMPLATE / rel).read_text(encoding="utf-8")
        for duplicated in ("/home/batchcom", "nvidia-smi", "df -h", "nohup", "ControlMaster", "~/.bashrc"):
            assert duplicated not in text, (rel, duplicated)
    remote = (TEMPLATE / ".opencode" / "agents" / "remote-exec.md").read_text(encoding="utf-8")
    assert "durable-terminal" in remote and "batchcom-host" in remote


def test_personal_journals_are_not_part_of_the_project_template():
    assert not (TEMPLATE / "notes" / "daily").exists()
    assert not (TEMPLATE / "notes" / "weekly").exists()
    assert not (TEMPLATE / "notes" / "templates").exists()

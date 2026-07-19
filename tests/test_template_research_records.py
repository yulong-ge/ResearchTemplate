"""Structural tests for research-record ownership in generated projects."""
from pathlib import Path


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
    assert "Do not create per-run Markdown or custom run JSON" in policy


def test_template_does_not_copy_global_skills():
    assert not (TEMPLATE / ".agents" / "skills").exists()

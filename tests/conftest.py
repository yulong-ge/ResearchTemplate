"""Pytest fixtures: a disposable mini template for command-level tests."""
from __future__ import annotations

import textwrap

import pytest


@pytest.fixture
def mini_template(tmp_path, monkeypatch):
    """A tiny template under RTMPL_TEMPLATES_ROOT for isolated command tests."""
    troot = tmp_path / "templates"
    tmpl = troot / "demo"
    (tmpl / "src").mkdir(parents=True)
    tmpl.joinpath("template.yaml").write_text(
        textwrap.dedent(
            """\
            name: demo
            display: Demo
            version: "0.1.0"
            variables:
              - { token: "<proj>", field: proj, render_files: ["pyproject.toml"], prompt: "proj", required: true, validation: '^[a-z]+$' }
            exclude: []
            """
        )
    )
    tmpl.joinpath("pyproject.toml").write_text('name = "<proj>"\n')
    tmpl.joinpath("AGENTS.md").write_text("# agents\n")
    tmpl.joinpath("binary.pdf").write_bytes(b"%PDF-1.4\n\x00\x00binary\x00data\n")
    monkeypatch.setenv("RTMPL_TEMPLATES_ROOT", str(troot))
    return tmpl

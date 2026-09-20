# ResearchTemplate

`ResearchTemplate` is a Python package and CLI for creating and safely updating BatchCom research projects.

```bash
uv run rtmpl list
uv run rtmpl init my-project --var conda_env=ml --no-input
cd my-project
uv run rtmpl status
uv run rtmpl resume
uv run rtmpl check
```

`rtmpl new` and `rtmpl init` are equivalent initialization commands; both print the files to fill first. `adopt`, `update`, `status`, and `repair` manage the copyable template and `.rtmpl/state.json`. `resume` prints the compact research handoff and `check` validates the research record contract. Updates classify file changes, back up before mutation, and preserve user edits. Research records declared `seed_only` in the manifest become project-owned after scaffolding and stay intact under `update --force`.

The generated workspace supports human or automatic Inner and Outer Loops. The selected mode is recorded in the research policy and finite decisions; direction, scope, budget, and final claims can still require human confirmation. Global `research-workflow` skills provide retrieval, ideation, writing, and recording guidance. The optional ARA compiler, session manager, and rigor reviewer build or inspect standalone artifacts, while `rtmpl` manages template state and the generated project follows its declared execution protocol.

See [the template guide](rtmpl/templates/batchcom-research/README.md), [research workflow](rtmpl/templates/batchcom-research/docs/research-workflow.md), and [ADRs](docs/adr/).

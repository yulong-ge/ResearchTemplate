# ResearchTemplate

`ResearchTemplate` is a Python package and CLI for creating and safely updating research
projects. `rtmpl` owns template lifecycle metadata and file synchronization; the generated
workspace uses a human-written Plan to authorize each task.

```bash
uv run rtmpl list
uv run rtmpl new my-project --var conda_env=ml --no-input
cd my-project
uv run rtmpl status
uv run rtmpl update --dry-run
```

The lifecycle commands are `list`, `new`/`init`, `update`, `status`, `adopt`, and `repair`.
`.rtmpl/config.yaml` stores template variables and `.rtmpl/state.json` stores the template
version and file hashes. Files outside the template tree are never managed, and user edits to
managed files require an explicit update decision.

The copyable workspace contains `docs/plans/`, `notes/`, `experiments/`, `literature/`, and
`paper/`. A human supplies context and allowed paths in a Plan, reviews the Agent's proposed
commands, and decides how results become notes, paper material, or follow-up Plans.

See [the template guide](rtmpl/templates/batchcom-research/README.md), [the ADR](docs/adr/0001-rtmpl-and-human-research-workflow.md), and [implementation plan](docs/plans/2026-09-22-rtmpl-human-workflow.md).

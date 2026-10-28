# Framework code standards

These are the framework's existing development rules. Research-workspace
collaboration belongs to the [copyable template](subsystems/workspace-template.md).

## Rules

| Rule | What to check |
| --- | --- |
| Use ADRs for architectural decisions and keep them in `docs/adr/`. | Apply the [documentation guide](README.md) criteria for ADRs and plans. |
| Keep copyable workspace files below `rtmpl/templates/batchcom-research/`. | Framework files and generated-workspace files stay within their respective boundaries. |
| Remove obsolete paths directly unless compatibility is explicitly requested. | No unrequested compatibility path remains. |
| Preserve unrelated working-tree changes and make small verified commits. | Verification and file scope match the change. |
| Run Python and tests with `uv`. | Use the framework environment; read the [environment lessons](../LESSONS.md) first. |
| Put reusable research logic, parsing, and result code in generated `src/`. | Human-facing command orchestration goes in `scripts/`; implementation helpers go in `scripts/internal/`. |
| Supply no default smoke/check phase or entrypoint in the research template. | Add one only for an explicitly requested workflow. |

## Acceptance criteria

Run from the framework repository root before delivery:

```bash
uv run pytest
```

For template changes, exercise `rtmpl list`, scaffold a disposable project with
`rtmpl new`, and verify `rtmpl status` plus update protection for user-edited
managed files. The existing [implementation plan](plans/2026-09-22-rtmpl-human-workflow.md)
provides the command forms:

```bash
uv run rtmpl list
uv run rtmpl new demo --var conda_env=ml --no-input
```

Run creation in a disposable directory. From the created project, use:

```bash
uv run --project /Users/macbookair/code/ResearchTemplate rtmpl status
uv run --project /Users/macbookair/code/ResearchTemplate rtmpl update --dry-run
```

Read the [non-interactive update lesson](../LESSONS.md#resolve-every-non-interactive-update-decision)
before resolving changed/orphaned paths. The
[2026-09-28 plan](plans/2026-09-28-research-workflow-simplification.md)
also lists `uv run ruff check rtmpl tests` and `git diff --check` among its checks.
Report checks that were not run as **not run**.

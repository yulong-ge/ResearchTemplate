# Copyable research workspace

## Responsibilities and boundaries

`rtmpl/templates/batchcom-research/` is the consumer-facing project template.
It contains ordinary human notes, Plans, and experiment output directories.
Keep framework-development rules in this repository's development documents
and research-workspace rules in the template's own `AGENTS.md`.

## Sources of truth

| Source | Responsibility |
| --- | --- |
| [Template manifest](../../rtmpl/templates/batchcom-research/template.yaml) | Payload variables and file set |
| [Template AGENTS.md](../../rtmpl/templates/batchcom-research/AGENTS.md) | Project context, authorization, collaboration and environment |
| [Template README](../../rtmpl/templates/batchcom-research/README.md) | Human-facing workspace layout |
| [Plans guide](../../rtmpl/templates/batchcom-research/docs/plans/README.md) | Task scope, outputs, budget, stop conditions |
| [Experiments guide](../../rtmpl/templates/batchcom-research/experiments/README.md) | Raw run outputs |
| [Notes guide](../../rtmpl/templates/batchcom-research/notes/README.md), [environment record](../../rtmpl/templates/batchcom-research/notes/environment.md) | Project-owned notes and environment |
| [Paper guide](../../rtmpl/templates/batchcom-research/paper/README.md), [external-code guide](../../rtmpl/templates/batchcom-research/external/README.md) | Manuscript and third-party-code boundaries |
| [`src/paths.py`](../../rtmpl/templates/batchcom-research/src/paths.py) | Project storage paths |

## Runtime, state, constraints, and compatibility

The workspace contains `docs/plans/`, `notes/`, `experiments/`, `literature/`,
and `paper/`. A human supplies context and allowed paths in a Plan, reviews
the Agent's proposed commands, and decides how results become notes, paper
material, or follow-up Plans. The template AGENTS and Plans guide own the
detailed execution and failure boundaries. CLI update state remains separate
from research progress; old research files require manual migration.

The [code standards](../code-standards.md) define source/script placement and
the absence of a default smoke/check entrypoint. Read the
[third-party capability lesson](../../LESSONS.md#keep-third-party-installation-within-its-requested-scope)
before changing bundled capabilities.

## Verification

Use the [template acceptance commands](../code-standards.md#acceptance-criteria).
[`test_template_workflow.py`](../../tests/test_template_workflow.py) and
[`test_template_paths.py`](../../tests/test_template_paths.py) check the minimal
workflow, removal of research ledgers, skill boundaries, and storage paths.

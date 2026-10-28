# Framework subsystem references

Read the relevant page before changing its behavior, then follow its source links.
The [ADR](../adr/0001-rtmpl-and-human-research-workflow.md) retains the architectural
decision; [plans](../README.md) retain implementation history.

| Subsystem | Responsibility | Reference |
| --- | --- | --- |
| CLI lifecycle | Discover, render, create, adopt, and repair template baselines | [Lifecycle](lifecycle.md) |
| Update protection | Classify managed paths and apply explicit update decisions | [Update protection](update-protection.md) |
| Copyable research workspace | Human Plans, project-owned notes, and experiment outputs | [Workspace template](workspace-template.md) |

## Existing design and research documents

| Document | Role |
| --- | --- |
| [ADR-0001](../adr/0001-rtmpl-and-human-research-workflow.md) | Accepted architecture and ownership boundaries |
| [2026-09-22 implementation plan](../plans/2026-09-22-rtmpl-human-workflow.md) | Implemented migration, verification record, downstream rollout |
| [2026-09-28 simplification plan](../plans/2026-09-28-research-workflow-simplification.md) | Follow-up checklist and review fixes |
| [2026-09-21 workflow-template research](../research/2026-09-21-open-source-research-workflow-templates.md) | Historical comparison; proposals here are not current CLI contracts |

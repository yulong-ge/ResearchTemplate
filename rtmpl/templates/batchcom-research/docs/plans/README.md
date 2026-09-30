# Human execution Plans

Create one Plan for each experiment or engineering task. The Plan is the human-provided entry
point and authorization boundary for the Agent.

## Suggested contents

- question or concrete task and success criteria;
- background, data, code entry points, and prior information;
- files the Agent may read;
- files the Agent may modify and where outputs belong;
- commands, environment, resource limits, budget, and stop conditions;
- choices that require approval before execution.

The Plan is ordinary Markdown. Use the structure that makes the task clear, and revise it after
reviewing the results when the next step needs updated context.

## File naming

Use date-prefixed names: `YYYY-MM-DD-<short-description>.md`.

Completed Plans may be moved to `docs/plans/archive/` by the human owner.

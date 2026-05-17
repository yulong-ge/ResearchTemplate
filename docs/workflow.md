# Skills-Driven ARA Workflow

## State Model

There are only two memory layers.

Active working memory:

- `research/`
- `literature/`
- `experiments/`

Derived provenance:

- `ara/`

Write to the active working memory during research. Update `ara/` only during epilogue.

## Bootstrap

Use when starting a project or pivoting to a new major question.

1. Use `brainstorming-research-ideas` or `creative-thinking-for-research` to generate or refine candidate directions.
2. If one candidate needs an isolated evaluation, launch a fresh subagent and run `idea-evaluator` there.
3. Once the main session adopts a direction, write the immediate problem in `research/current-task.md`.
4. Summarize the project question, hypotheses, and status in `research/state.yaml`.
5. Update `research/exploration-tree.yaml` with the chosen branch.
6. Search literature and create durable notes in `literature/notes/`.
7. Update `literature/survey.md` with synthesized takeaways.

Use `literature/survey.md` as the aggregate map. Create a standalone note only when a paper contributes multiple concrete numbers, design choices, ablations, or implementation constraints that the project will reuse.

## Inner Loop

Use for fast experiment cycles.

1. Choose one hypothesis.
2. If confirmatory, write a protocol first in `experiments/protocols/`.
3. Run the experiment or implementation task.
4. Save meaningful results in `experiments/results/<experiment-id>/` or external trackers.
5. Write a human-readable record in `experiments/logs/`.
6. Update `research/state.yaml` with trajectory changes.

If a hypothesis becomes a long-lived branch with multiple related experiments, create `experiments/<hypothesis-slug>/` and keep branch-level protocol, code, results, and analysis there. Use the shared `experiments/protocols/`, `experiments/logs/`, and `experiments/results/` paths for cross-branch indexing and lightweight records.

Use `research/exploration-tree.yaml` as the live control tree while the project is active. Treat `ara/trace/exploration_tree.yaml` as epilogue-only archival output produced by `ara-research-manager`.

`data/` is for local inputs, cached analysis assets, downloaded metadata, or reference statistics. Do not use it as a second experiment-results directory.

## Outer Loop

Use after several experiments or when patterns emerge.

1. Review recent experiment logs and literature notes.
2. Update `research/findings.md`:
   - current understanding
   - patterns and insights
   - lessons and constraints
   - open questions
3. Update `research/exploration-tree.yaml` when a branch deepens, fails, or pivots.
4. Revise hypotheses or current direction in `research/state.yaml`.

## Epilogue

Use only after an outer-loop update, a direction pivot, or the end of a session that changed the next actionable step.

1. Run `ara-rigor-reviewer` if important claims were made.
2. Run `ara-research-manager` to translate the session into `ara/` provenance records.
3. If external material needs ingestion into ARA form, use `ara-compiler`.

## Paper Flow

When the research story is mature:

1. Make sure `research/findings.md` contains a stable claim-and-evidence narrative.
2. Organize manuscript assets and section drafts under `paper/`.
3. Use `ml-paper-writing` to draft and refine the paper.
4. Keep figures, tables, and citations aligned with the evidence recorded in `research/`, `literature/`, and `experiments/`.

## Autonomy Boundary

In this workspace:

1. Do not start recurring `/loop`, cron, watchdog, or heartbeat processes unless the user explicitly asks for them.
2. Do not generate recurring progress decks or status-report folders unless explicitly requested.
3. Use the two-loop research logic, but keep execution session-scoped and user-directed by default.

## Design Principle

The project should stay operable even if the agent ignores one helper file. That is why the workflow relies on a small number of durable markdown/YAML files instead of a larger orchestration layer.

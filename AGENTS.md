# Skills-Driven ARA Research Workspace

## Research Agent Operating Guide

### Start Here

1. Read `research/state.yaml`, `research/findings.md`, and `research/current-task.md` first.
2. Treat `research/`, `literature/`, and `experiments/` as the active working memory.
3. Treat `ara/` as epilogue output only.
4. Load `autoresearch` when the task involves iterative research planning, experiments, and synthesis across multiple hypotheses.

### How To Work

- Keep the main research question, hypotheses, and next step in `research/state.yaml`.
- Keep synthesized technical understanding in `research/findings.md`.
- Keep project-level progress in `research/research-log.md`.
- Keep branch and hypothesis structure in `research/exploration-tree.yaml`.
- Save paper notes in `literature/notes/` and maintain the aggregate map in `literature/survey.md`.
- Write confirmatory protocols in `experiments/protocols/` before running experiments.
- Save meaningful run records in `experiments/logs/` and shared structured outputs in `experiments/results/<experiment-id>/`.
- Use the top-level `experiments/protocols/`, `experiments/logs/`, and `experiments/results/` paths as the project-wide index for lightweight runs, cross-branch records, and standardized exports.
- When one outer-loop hypothesis becomes its own sustained branch, create `experiments/<hypothesis-slug>/` and keep that branch's protocol, experiment-specific code, results, and analysis there.

### Rules

- For a new direction, generate or refine candidate ideas with `brainstorming-research-ideas` or `creative-thinking-for-research` first.
- Use `idea-evaluator` only after a candidate idea already exists and needs an isolated evaluation.
- Run `idea-evaluator` in a fresh subagent so the evaluation is not mixed with the active working context.
- After an `idea-evaluator` subagent returns, the main session decides whether to adopt the result and, if adopted, records the conclusion in `research/research-log.md` and updates `research/state.yaml`, `research/current-task.md`, and `research/exploration-tree.yaml` as needed.
- Use `ara-rigor-reviewer` before treating an important claim as established.
- Use `ara-research-manager` only after an outer-loop update, a direction pivot, or the end of a work unit that changed the next actionable step.
- Do not start recurring `/loop`, cron, watchdog, or heartbeat jobs unless the user explicitly asks for continuous autonomous operation.

### Directory Boundaries

- `data/` is for local inputs, cached analysis assets, downloaded metadata, or reference statistics, not experiment outputs.
- `to_human/` is for optional human-facing summaries, decks, or reports when explicitly useful.
- `paper/` is for manuscript assets and section drafts only.
- Keep reusable code in `src/`, not buried inside one experiment folder.
- `research/exploration-tree.yaml` is the live tree for active research. `ara/trace/exploration_tree.yaml` is epilogue-only archive state and should not be updated during active research.

### Deep Learning Discipline

- Use conda, never the `base` environment, for deep-learning work.
- Check GPU and storage before large training or downloads.
- Do not silently swallow critical model, data, checkpoint, or config failures.

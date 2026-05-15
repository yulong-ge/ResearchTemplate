# Skills-Driven ARA Research Workspace

## Part 1: New Project Initialization

Use this section only when this repository has just been copied to start a new research project.

1. Replace the placeholders in `research/state.yaml`, `research/current-task.md`, `research/findings.md`, `research/research-log.md`, `research/exploration-tree.yaml`, and `literature/survey.md` with the real project information.
2. Remove any placeholder or starter content in `literature/notes/`, `experiments/protocols/`, `experiments/logs/`, `experiments/results/`, `paper/`, and `ara/` that does not belong to the new project.
3. Restore managed skills from `skills-lock.json` if they are missing.
4. After initialization is complete, delete this entire `Part 1: New Project Initialization` section from `AGENTS.md` and keep only Part 2.

## Part 2: Research Agent Operating Guide

### Start Here

1. Read `research/state.yaml`, `research/findings.md`, and `research/current-task.md` first.
2. Treat `research/`, `literature/`, and `experiments/` as the active working memory.
3. Treat `ara/` as epilogue output only.

### How To Work

- Keep the main research question, hypotheses, and next step in `research/state.yaml`.
- Keep synthesized technical understanding in `research/findings.md`.
- Keep project-level progress in `research/research-log.md`.
- Keep branch and hypothesis structure in `research/exploration-tree.yaml`.
- Save paper notes in `literature/notes/` and maintain the aggregate map in `literature/survey.md`.
- Write confirmatory protocols in `experiments/protocols/` before running experiments.
- Save meaningful run records in `experiments/logs/` and structured outputs in `experiments/results/<experiment-id>/`.

### Rules

- For a new direction, use `idea-evaluator` first.
- Use `ara-rigor-reviewer` before treating an important claim as established.
- Use `ara-research-manager` only after an outer-loop update, a direction pivot, or the end of a work unit that changed the next actionable step.
- Do not start recurring `/loop`, cron, watchdog, or heartbeat jobs unless the user explicitly asks for continuous autonomous operation.

### Directory Boundaries

- `data/` is for local inputs, cached analysis assets, downloaded metadata, or reference statistics, not experiment outputs.
- `paper/` is for manuscript assets and section drafts only.
- Keep reusable code in `src/`, not buried inside one experiment folder.

### Deep Learning Discipline

- Use conda, never the `base` environment, for deep-learning work.
- Check GPU and storage before large training or downloads.
- Do not silently swallow critical model, data, checkpoint, or config failures.

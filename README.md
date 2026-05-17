# Skills-Driven ARA Research Template

This repository is a directly usable research workspace for deep learning, generative modeling, and interpretability projects driven by OpenCode skills.

It keeps active research memory in `research/`, `literature/`, and `experiments/`, and uses `ara/` only as an epilogue provenance layer.

## Directory Layout

```text
.agents/skills/                  # Managed and local research skills
.opencode/                       # Optional local OpenCode commands/config helpers
AGENTS.md                        # Project-level operating rules for agents
opencode.jsonc                   # Academic MCP configuration
skills-lock.json                 # Managed skills source lockfile

research/
  state.yaml                     # Active question, hypotheses, loop status
  findings.md                    # Current technical understanding and synthesized lessons
  research-log.md                # Chronological project-level research log
  exploration-tree.yaml          # Active hypothesis / branch structure
  current-task.md                # Current task / immediate objective

literature/
  survey.md                      # Running survey synthesis
  notes/                         # One note per paper

experiments/
  protocols/                     # Protocol before confirmatory runs
  logs/                          # One human-readable record per meaningful run
  results/                       # Shared structured outputs, summaries, tables across branches
  <hypothesis-slug>/             # Optional per-direction experiment workspace
    protocol.md                  # Direction-level protocol and prediction
    code/                        # Experiment-specific code when it should not live in src/
    results/                     # Direction-scoped outputs and analysis artifacts
    analysis.md                  # What this branch taught the project

src/                             # Reusable code written during research
data/                            # Local inputs, cached analysis assets, reference stats
paper/                           # Draft paper assets and sections
ara/                             # Derived provenance package, updated only in epilogue
docs/
  workflow.md                    # How to use the template
```

## What This Workspace Does

- Keeps project state, findings, and immediate priorities in `research/`
- Stores durable paper notes in `literature/notes/` and a rolling synthesis in `literature/survey.md`
- Separates confirmatory protocols, run logs, and structured outputs inside `experiments/`
- Reserves `src/` for reusable code and `data/` for local inputs and cached assets
- Uses `ara/` only after meaningful research progress has been synthesized

## Core Design

This template follows a simple memory model.

Canonical working memory:

- `research/state.yaml`
- `research/findings.md`
- `research/research-log.md`
- `research/exploration-tree.yaml`
- `literature/`
- `experiments/`

Derived provenance memory:

- `ara/`

`ara/` is updated only after an outer-loop update, a direction pivot, or the end of a session that changed the next actionable step via `ara-research-manager`. It is not the place the agent should write first while actively researching.

## Normal Research Flow

1. If the direction is still unclear, use `brainstorming-research-ideas` or `creative-thinking-for-research` to generate or refine candidate ideas.
2. If one candidate needs a structured go/no-go judgment, launch a fresh subagent and run `idea-evaluator` there.
3. After the main session accepts a direction, update `research/current-task.md`, `research/state.yaml`, and `research/exploration-tree.yaml`.
4. Search literature and save durable notes under `literature/notes/`, then update `literature/survey.md`.
5. For confirmatory work, write a protocol under `experiments/protocols/` before running.
6. When a hypothesis becomes its own sustained branch, create `experiments/<hypothesis-slug>/` to hold that branch's protocol, code, results, and analysis.
7. Run the inner loop: execute, measure, log, interpret.
8. Update `experiments/logs/`, `research/findings.md`, and `research/research-log.md`.
9. Periodically run the outer loop: synthesize patterns, revise hypotheses, pivot if needed.
10. After an outer-loop update, a direction pivot, or the end of a session that changed the next actionable step, run `ara-research-manager` to compile provenance into `ara/`.

The goal is to keep the research workflow direct while preserving structured memory, literature discipline, protocol-before-result, and provenance capture.

Top-level `experiments/protocols/`, `experiments/logs/`, and `experiments/results/` are the shared experiment index for the whole project. Use them for lightweight runs, cross-branch records, and standardized result exports. Promote a direction into `experiments/<hypothesis-slug>/` only when that hypothesis becomes a sustained branch with its own code, accumulated results, and analysis.

`research/exploration-tree.yaml` is the live control tree for active research. `ara/trace/exploration_tree.yaml` is the epilogue-only archive of explored directions and should be updated only through `ara-research-manager`.

## Start a New Project

```bash
cp -R skills-driven-ara-template <new-project>
cd <new-project>
git init
```

If managed skills are present in `skills-lock.json`, restore them before the first OpenCode run:

```bash
npx skills experimental_install
```

The project expects the managed skills listed in `skills-lock.json` to exist under `.agents/skills/`. If they are missing, restore them first instead of editing workflow documents to work around the absence.

Then open the project with OpenCode. `README.md` explains the workspace layout for humans; `AGENTS.md` tells the agent how to operate inside the project.

## Managed Skills

Managed skills from AI-Research-SKILLs are tracked in `skills-lock.json` so updates remain source-aware and reproducible.

## Agent Entry Point

When an OpenCode agent starts working in this repository, it should follow `AGENTS.md` first. That file defines:

- which files to read before starting research work
- where to record state, findings, protocols, logs, and outputs
- which rules govern autonomy, provenance, and deep-learning execution discipline

## Important Rules

- Protocol before result for confirmatory experiments.
- Never hallucinate citations or BibTeX.
- Use WandB for metric history when needed; use project files for interpretation and decisions.
- Do not silently swallow critical dataset, model, checkpoint, or config failures.
- Treat `ara/` as epilogue output, not active scratch space.

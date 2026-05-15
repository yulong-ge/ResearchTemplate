# Skills-Driven ARA Research Template

This template is a deep-learning research workspace driven by skills and ARA.

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
  results/                       # Small structured outputs, summaries, tables

src/                             # Reusable code written during research
data/                            # Local inputs, cached analysis assets, reference stats
paper/                           # Draft paper assets and sections
ara/                             # Derived provenance package, updated only in epilogue
docs/
  workflow.md                    # How to use the template
```

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

1. Define or update the current objective in `research/current-task.md`.
2. If the direction is new, use `idea-evaluator` before committing to it.
3. Search literature and save durable notes under `literature/notes/`, then update `literature/survey.md`.
4. Record hypotheses and loop state in `research/state.yaml`.
5. For confirmatory work, write a protocol under `experiments/protocols/` before running.
6. Run the inner loop: execute, measure, log, interpret.
7. Update `experiments/logs/`, `research/findings.md`, and `research/research-log.md`.
8. Periodically run the outer loop: synthesize patterns, revise hypotheses, pivot if needed.
9. After an outer-loop update, a direction pivot, or the end of a session that changed the next actionable step, run `ara-research-manager` to compile provenance into `ara/`.

The goal is to keep the research workflow direct while preserving structured memory, literature discipline, protocol-before-result, and provenance capture.

## Start a New Project From This Template

```bash
cp -R ~/code/skills-driven-ara-template <new-project>
cd <new-project>
git init
```

If managed skills are present in `skills-lock.json`, restore them before the first OpenCode run:

```bash
npx skills experimental_install
```

The template expects the managed skills listed in `skills-lock.json` to exist under `.agents/skills/`. If they are missing, restore them first instead of editing workflow documents to work around the absence.

Then open the project with OpenCode and work directly from `AGENTS.md` plus `docs/workflow.md`.

## Managed Skills

Managed skills from AI-Research-SKILLs are tracked in `skills-lock.json` so updates remain source-aware and reproducible.

## Important Rules

- Protocol before result for confirmatory experiments.
- Never hallucinate citations or BibTeX.
- Use WandB for metric history when needed; use project files for interpretation and decisions.
- Do not silently swallow critical dataset, model, checkpoint, or config failures.
- Treat `ara/` as epilogue output, not active scratch space.

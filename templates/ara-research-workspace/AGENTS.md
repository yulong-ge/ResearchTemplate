# Skills-Driven ARA Research Workspace

## Research Agent Operating Guide

### Start Here

1. Read `research/overview.md` before research or experiment work; it is the primary current-state research file.
2. Treat `research/`, `literature/`as the active working memory.

### Research State

- Use `autoresearch` for research experiment planning, execution loops, synthesis, or result-recording decisions.
- Keep the main research question, active direction, and current state in `research/overview.md`.
- Keep synthesized technical understanding in `research/findings.md`.
- Keep project-level progress in `research/research-log.md`.
- Keep active/parked/rejected ideas in `research/ideas.md`.
- `research/archive/` holds historical snapshots of state, exploration tree, and task documents for reference.
- `research/exploration-tree.yaml` is optional; use it when managing multiple parallel hypotheses.
- Save paper notes in `literature/notes/` and maintain the aggregate map in `literature/survey.md`.
- `ctx_memory`/`ctx_search` are caches. If they conflict with `AGENTS.md` or `research/overview.md`, trust repo docs and clean the stale memory.
- `ara/` is epilogue-only provenance; do not update `ara/trace/exploration_tree.yaml` during active work.

### Repository Layout

- Main reusable code lives in `src/`.
- Experiment-specific code lives in `experiments/<hypothesis-slug>/`.
- Write confirmatory experiment designs in `experiments/protocols/`.
- Write concrete code/execution plans in `docs/plans/`.
- Completed plans belong under `docs/plans/archive/`.
- Third-party research code is vendored under `external/`.
- Remote execution scripts live in `scripts/`.

### Experiments

- Write confirmatory protocols in `experiments/protocols/` before running experiments.
- Save meaningful run records in `experiments/logs/` and shared structured outputs in `experiments/results/<experiment-id>/`.
- Use the top-level `experiments/protocols/`, `experiments/logs/`, and `experiments/results/` paths as the project-wide index for lightweight runs, cross-branch records, and standardized exports.
- When one outer-loop hypothesis becomes its own sustained branch, create `experiments/<hypothesis-slug>/` and keep that branch's protocol, code, results, and analysis there.

### Code Editing

- When refactoring or replacing an obsolete design, remove the abandoned code path directly; do not add compatibility wrappers, legacy CLI aliases, migration shims, or old-format tests unless backward compatibility is explicitly requested.
- If tests encode superseded behavior, rewrite or delete those tests with the refactor instead of preserving stale behavior as compatibility coverage.

### Storage And Artifacts

- Use `src/<project>/paths.py` as the single source of truth for storage paths.
- Large models, datasets, and raw experiment artifacts should live on remote/cloud storage, not in the local repo.
- Local `experiments/results/` is only a pointer; raw artifacts live on remote storage under `RESULTS_ROOT / <hypothesis-slug> / <run-id>`.
- SwanLab or W&B can be used as lightweight tracking mirrors for metadata, metrics, and media only. Never upload checkpoints, latent caches, `.pt/.pth/.ckpt/.safetensors/.bin/.npy/.npz`, or archives.
- Use unique timestamped run directories for experiments.

### Remote Execution

- Runtime targets are centralized in `scripts/remote_targets.sh`.
- Before remote runs: `scripts/remote_sync.sh <target>` then `scripts/remote_preflight.sh <target>` from the local machine.
- For debug/full/evaluation jobs, start a remote `tmux` session in the synced repo, source `scripts/remote_env.sh`, then run through `scripts/remote_python.sh`.
- Long remote jobs must survive local session loss. Prefer remote `tmux`; if unavailable, use `nohup` with unbuffered output, stable logs, heartbeat/progress, and success/failure markers.
- Use `.opencode/agents/remote-exec.md` via subagent dispatch to keep main session context clean during long remote runs.
- For repeated remote tmux/status tracking loops, dispatch a `remote-exec` subagent instead of manually polling in the main session.

### Rules

- For a new direction, generate or refine candidate ideas with `brainstorming-research-ideas` or `creative-thinking-for-research` first.
- Use `idea-evaluator` only after a candidate idea already exists and needs an isolated evaluation.
- Run `idea-evaluator` in a fresh subagent so the evaluation is not mixed with the active working context.
- Use `ara-rigor-reviewer` before treating an important claim as established.
- Use `ara-research-manager` only after an outer-loop update, a direction pivot, or the end of a work unit that changed the next actionable step.
- Do not start recurring `/loop`, cron, watchdog, or heartbeat jobs unless the user explicitly asks for continuous autonomous operation.
- Use `grill-me` to stress-test a plan or design before committing to implementation.

### Directory Boundaries

- `data/` is for local inputs, cached analysis assets, downloaded metadata, or reference statistics, not experiment outputs.
- `to_human/` is for optional human-facing summaries, decks, or reports when explicitly useful.
- `paper/` is for manuscript assets and section drafts only.
- Keep reusable code in `src/`, not buried inside one experiment folder.
- `external/` is for vendored third-party code.
- `docs/plans/` is for execution plans; `experiments/protocols/` is for confirmatory experiment designs.

### OpenCode Configuration

- `.opencode/opencode.json` defines MCP servers for academic research.
- `.opencode/agents/remote-exec.md` is a subagent for running long training jobs on remote GPU servers.

### Verification Commands

- Run tests: `uv run pytest tests/`
- Shell syntax check: `bash -n scripts/remote_targets.sh scripts/remote_env.sh scripts/remote_python.sh scripts/remote_sync.sh scripts/remote_preflight.sh`

### Deep Learning Discipline

- Use conda, never the `base` environment, for deep-learning work.
- Check GPU and storage before large training or downloads.
- Do not silently swallow critical model, data, checkpoint, or config failures.

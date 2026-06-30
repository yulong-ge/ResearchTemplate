# ResearchKit Template Framework

This repository develops a copyable research workspace template and its `rk` runtime.

The root is for framework development. The actual project template lives in:

```text
templates/ara-research-workspace/
```

## Target Layout

This is the intended framework shape for the batchcom RK-lite implementation. Some paths may be introduced by the implementation plan rather than already present.

```text
AGENTS.md                         # Framework-development guide for agents
docs/                             # Framework design records, ADRs, and plans
  adr/                            # Architecture decision records
  handoffs/                       # Session handoff documents
  plans/                          # Framework implementation plans
rk/                               # RK-lite framework tool source
templates/
  ara-research-workspace/         # Copyable research project template
    AGENTS.md                     # Agent guide inside copied projects
    .rk/                          # Project-level rk config template
    .agents/                      # Managed research skills
    .opencode/                    # OpenCode project configuration
    scripts/                      # Research-project execution helpers
    remote/                       # Target/server profile docs and configs
    research/                     # Active research memory
    literature/                   # Paper survey and notes
    experiments/                  # Protocols, logs, results
    src/                          # Downstream research code only
```

## Start A Research Project

From this framework repository:

```bash
cp -R templates/ara-research-workspace <new-project>
cd <new-project>
git init
```

Replace every `CHANGE_ME` in `.rk/project.toml` with the project slug before the first run, then check the resolved paths:

```bash
perl -pi -e 's/CHANGE_ME/<project-slug>/g' .rk/project.toml
rk doctor
```

Then open the copied project with OpenCode or Codex and follow its `AGENTS.md`.

## Template Summary

The copied workspace keeps active research memory in `research/`, paper notes in `literature/`, and experiment protocols/logs/results in `experiments/`. It reserves `src/` for downstream research code and treats `ara/` as epilogue provenance output.

The current template is tuned for batchcom with Git-first synchronization and RK-lite execution:

- canonical project root: `/home/dataset-assist-0/research/<project>`
- optional scratch root: `/home/dataset-local/<project>`
- project path config: `.rk/project.toml`
- execution wrapper: `rk run <launcher> ...`

## Development Notes

Use root `docs/adr/` for architecture decisions and root `docs/plans/` for implementation plans. Consumer-facing workflow docs belong under `templates/ara-research-workspace/docs/`.

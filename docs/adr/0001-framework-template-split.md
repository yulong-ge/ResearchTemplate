# ADR 0001: Split Framework Development From Copyable Template

## Status

Accepted.

## Context

The old repository root was a directly usable research workspace. That made two agent audiences share one set of instructions:

- agents developing the template/framework itself
- agents operating inside a copied research project

The historical handoff originally recorded the decision to turn the repository into a framework source tree while keeping the actual research workspace as a nested copyable template. ADR 0002 and the batchcom RK-lite design are authoritative for current runtime placement.

## Decision

Keep framework-development files at the repository root and move the copyable research workspace to `templates/ara-research-workspace/`.

Root `AGENTS.md` describes framework development. Template `AGENTS.md` describes research-project operation after the template is copied.

Framework design records live in root `docs/`. Consumer-facing workflow documentation lives under `templates/ara-research-workspace/docs/`.

ADR 0002 supersedes the original runtime placement: `rk` source lives at the framework repository root, while copied projects contain only project-level `.rk/` configuration.

## Consequences

- The repository can evolve the framework without confusing copied-project agents.
- The template can be copied as a self-contained research workspace.
- Changes that affect the framework/template boundary should get new ADRs.

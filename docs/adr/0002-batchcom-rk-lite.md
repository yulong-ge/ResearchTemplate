# ADR 0002: batchcom Git-first RK-lite

## Status

Accepted.

## Context

The batchcom remote is the current target environment. The previous remote-sync design introduced too much complexity because one-way Mac-to-server synchronization makes server edits non-authoritative and easy to overwrite. The current direction is to use GitHub/Git as the code synchronization source of truth and keep `rk` as a small execution safety layer.

## Decision

Implement v1 as batchcom-specific RK-lite:

- code sync uses Git, not Mutagen
- `rk` source lives at the framework repository root
- copied projects contain `.rk/project.toml`, not `rk` source
- project `src/` is reserved for downstream research code
- `/home/dataset-assist-0/research/<project>` is canonical storage
- `/home/dataset-local/<project>` is optional explicit scratch storage
- SSH and SSH MCP configs are read-only inputs to `rk`

This supersedes ADR 0001's original runtime-source placement. `rk` no longer lives inside `templates/ara-research-workspace/src/rk/`; copied project `src/` is reserved for downstream research code.

## Consequences

- This v1 batchcom implementation remains simple and avoids a general multi-remote abstraction.
- Mac-local MCP tooling remains the primary rich agent environment.
- Server-side edits are allowed, but must use Git commit/push/pull.
- Future remotes can get separate designs when concrete requirements appear.

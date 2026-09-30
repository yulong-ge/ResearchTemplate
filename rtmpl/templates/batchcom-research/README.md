# BatchCom research project

This template provides a small human and Agent collaboration workspace. `rtmpl` manages only
template lifecycle files. A human supplies the context and Plan for each task; the Agent proposes
and executes an approved set of changes, then reports the resulting artifacts.

## Directory layout

| Location | Purpose |
|---|---|
| `docs/plans/` | Human-written task Plans and approvals |
| `notes/` | Human-maintained background, environment, and provenance notes |
| `experiments/` | Results, logs, configurations, and raw artifacts |
| `literature/` | Paper notes and references |
| `paper/` | Manuscript assets |
| `.rtmpl/` | Template name, variables, version, and file hashes |

## One task at a time

1. Create `docs/plans/YYYY-MM-DD-<description>.md` with the question, context, allowed files,
   commands, resource limits, and stop conditions.
2. Ask the Agent to propose an execution plan. Review the file list and approve the exact task.
3. Let the Agent edit only the approved code/configuration paths and write the requested outputs
   under a human-chosen `experiments/<name>/` directory.
4. Review raw outputs and organize notes, interpretations, and follow-up Plans yourself.

Each project can choose the amount of structure that helps its work. The human Plan defines the
directory name, expected outputs, and any additional record format for that task.

For note organization, see [human-note-organization.md](docs/human-note-organization.md).

The Zotero MCP is configured for the local Zotero API through `ZOTERO_LOCAL=true`.
It uses the Zotero desktop database on `localhost`; this template does not need a
Web API key or library ID.

## Storage

Import storage roots from `src/paths.py`. Shared assets use `SHARED_DATA_ROOT` and
`SHARED_MODEL_ROOT`; project assets use `DATA_ROOT`, `MODEL_ROOT`, and `RESULTS_ROOT`.
`DATA_CACHE` and `LIB_CACHE` are disposable caches, not canonical asset locations.

# Template lifecycle

## Responsibilities and boundaries

`rtmpl` creates and updates Git-first research projects. It owns template
lifecycle commands and hash-protected file updates. Generated projects use
human-written Plans to define experiment execution and storage workflows.
The CLI does not model research objects, automation modes, or note ownership.

## Sources of truth and runtime paths

| Source and symbols | Role |
| --- | --- |
| [`build_parser`, `main`](../../rtmpl/cli.py) | Commands: `list`, `new`/`init`, `update`, `status`, `adopt`, `repair` |
| [`TemplateManifest`, `load_manifest`, `walk_payload`](../../rtmpl/core/template.py) | Discovery, manifest validation, payload boundaries |
| [`validate_values`, `render_payload`, `check_render_residuals`](../../rtmpl/core/render.py) | Declared variables and rendering |
| [`new.run`](../../rtmpl/commands/new.py), [`adopt.run`](../../rtmpl/commands/adopt.py), [`repair.run`](../../rtmpl/commands/repair.py) | Creation, existing-project baselines, state repair |

The parser dispatches a lifecycle command. Creation loads the manifest,
collects variables, renders the payload, and establishes the template baseline.
The [update subsystem](update-protection.md) owns subsequent synchronization.

## State, constraints, failures, and compatibility

`.rtmpl/config.yaml` stores template variables; `.rtmpl/state.json` stores
the template version and file hashes. The [ADR](../adr/0001-rtmpl-and-human-research-workflow.md)
defines the metadata contract, safe-path checks, manifest validation, and
`init` compatibility alias. Invalid paths, manifests, or render values fail
through the linked validation code; the CLI does not interpret research
notes or create research conclusions.

## Verification

Use the [acceptance commands](../code-standards.md#acceptance-criteria).
[`test_commands.py`](../../tests/test_commands.py) covers command surface,
creation, adoption, and repair; [`test_core.py`](../../tests/test_core.py)
covers manifests, rendering, and state.

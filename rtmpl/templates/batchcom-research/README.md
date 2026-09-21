# BatchCom research project

This template keeps reusable methods in global Skills and keeps research facts in the project. `rtmpl` manages the template lifecycle; experiment execution follows the project protocol and the selected tracker.

## Record ownership

| Location | Owns |
|---|---|
| `research-state.yaml` | compact current state, object IDs, relations, automation_mode override, and next action |
| `to_human/latest.md` | the only daily human reading entry |
| `to_human/dashboard.html` | generated single-page view rebuilt by `src/dashboard_builder.py`; not a source of truth |
| `hypotheses.md` | H hypotheses, predictions, sources, and status |
| `findings.md` | Outer Loop synthesis and open questions |
| `claims.md` | C claims, scope, evidence for/against, and revisions |
| `decisions.md` | D direction decisions and finite experiment authorizations |
| `research-log.md` | concise Inner/Outer Loop timeline |
| `research/policy.yaml` | default automation_mode and human confirmation rules |
| `experiments/<topic>-<seq>/` | protocol, committed config, result summary, and analysis |
| `literature/` | survey and paper notes |
| `paper/` | manuscript assets |

Run-level metrics, logs, media, configs, and artifacts belong to the selected tracker and durable results store. `to_human/` graphs and trajectories are derived views and are never a second source of truth.

## Lifecycle

1. Record a candidate H and its prediction.
2. Write and lock an experiment protocol and config under `experiments/<topic>-<seq>/`, then attach an approved D authorization.
3. Run the declared scope. `automation_mode` (`manual`/`semi-auto`/`full-auto`) sets how much of the Inner and Outer Loops runs without human confirmation, per policy and the active decision.
4. Record the result and validity checks, then update `research-state.yaml`, `findings.md`, and `to_human/latest.md`.
5. Revise C claims or record a D decision only when the evidence and required human review support it.

When applying a newer template, `rtmpl` seeds the new record homes and preserves project-owned prose. Migrate natural-language content manually, carrying IDs and uncertainty forward instead of asking the template tool to infer meaning.

Use the global `research-record` skill for routing. ARA is opt-in through `ara-compiler` or `ara-session-manager`; it produces a standalone artifact alongside this project’s records.

## Storage

Import storage roots from `src/paths.py`. Shared assets use `SHARED_DATA_ROOT` and `SHARED_MODEL_ROOT`; project assets use `DATA_ROOT`, `MODEL_ROOT`, and `RESULTS_ROOT`. `DATA_CACHE` and `LIB_CACHE` are disposable caches.

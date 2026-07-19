# BatchCom research project

This template keeps reusable research methods in global Skills and keeps concrete record ownership in the repository. Do not copy global Skills into the project. Add a project-level Skill only when the project needs rules that differ from this default.

## Record ownership

Each fact has one home. Other documents use short links rather than copied narratives.

| Location | Owns |
|---|---|
| `research/overview.md` | current status, blocker, next action, pending decision, and links |
| `research/ideas.md` | unapproved hypotheses, predictions, and parked directions |
| `research/decisions.md` | durable approved choices and rationale across experiments |
| `research/findings.md` | mature cross-experiment conclusions and open scientific questions |
| `research/environment.md` | verified environment, data, model, and storage facts |
| `research/log.md` | concise research milestones with links |
| `experiments/<id>/protocol.md` | experiment question, scope, conditions, metrics, validity, and amendments |
| `experiments/<id>/config.yaml` | committed executable experiment configuration |
| `experiments/<id>/analysis.md` | milestone results, tracker references, anomalies, and interpretation |
| `literature/` | literature survey and paper notes |
| `paper/` | manuscript assets |

Run-level config, metrics, logs, media, and manifests belong to the selected tracker and durable results store. Do not create per-run Markdown or custom run JSON in Git unless a project-level policy explicitly adopts that model.

## Research lifecycle

1. Record candidate directions in `research/ideas.md`.
2. Create `experiments/<id>/protocol.md` and committed `config.yaml` when an experiment is ready to define.
3. Run from identifiable code and let the tracker/results store own run-level evidence.
4. Summarize only meaningful milestones in `analysis.md`; add a one-line pointer to `research/log.md` when useful.
5. Promote only durable cross-experiment knowledge into `research/findings.md` or `research/decisions.md`.

Use the global `research-record` Skill for routing and reconciliation. It must discover and follow this repository policy rather than supply paths of its own. If a downstream project changes ownership, record the replacement in project `AGENTS.md` or a project-specific Skill.

## Storage

`src/paths.py` is the executable source for storage roots. Shared assets use `SHARED_DATA_ROOT` and `SHARED_MODEL_ROOT`; project assets use `DATA_ROOT` and `MODEL_ROOT`; durable outputs use `RESULTS_ROOT`. `DATA_CACHE` and `LIB_CACHE` are disposable acceleration layers, never the unique copy.

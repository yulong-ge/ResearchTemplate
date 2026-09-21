# ADR-0008: ADHD-optimized template contract

- Status: Accepted
- Date: 2026-09-21

## Decision

The BatchCom template adopts four contract changes aimed at lowering the
resume cost of an interrupted research session.

Experiments stop using the `E<id>` letter prefix. Directory names, the `id`
fields in `protocol.md` and `config.yaml`, and the `objects.experiments` list
in `research-state.yaml` all use a lowercase semantic label `<topic>-<seq>`
(for example `batch-size-01`). Other object kinds keep their letter prefixes:
H, R, F, C, D.

`loop_control.inner`/`loop_control.outer` are replaced by a single
`automation_mode`. `research/policy.yaml` sets the default and
`research-state.yaml` may carry a project-level override; a direction decision
may still set a finite override. `manual` requires human confirmation for both
loops, `semi-auto` runs the Inner Loop inside an approved finite scope and
confirms the Outer Loop, and `full-auto` runs both loops for repetitive
validation only. `allow_manual_override` is kept.

`to_human/latest.md` gains a resume checklist and a status-badge emoji
convention (blue candidate, green active, yellow waiting, white closed) and
drops the `estimate_minutes` field so the state file stays a pure index.
`to_human/dashboard.html` is a generated single-page view rebuilt by
`src/dashboard_builder.py` from the state file and records; like the Mermaid
and trajectory views it is never a second source of truth.

`rtmpl` gains workflow hooks rather than new ledgers: `rtmpl pause` writes
`to_human/paused-context.md`, `rtmpl resume` prints paused context before the
state header and human brief, `rtmpl check --consistency` verifies the index,
relations, and experiment directories agree, `rtmpl doctor` reports unfilled
seed files, and `rtmpl summary` opens or prints the dashboard.

## Consequences

- A resumed agent reads three small files plus a paused-context note instead
  of reconstructing the whole repository.
- Semantic labels are self-describing in the index, the directory tree, and
  every relation, at the cost of enforcing a naming convention at check time.
- One automation knob is easier to set and to audit than two per-loop modes,
  and the semantics map directly onto the two-loop rhythm.
- Fill-in-the-blank record templates reduce blank-page paralysis; the
  placeholders are replaced by real content, not treated as schema.
- All views under `to_human/` remain derived and regenerable; the records
  stay the only source of truth.

## Rejected scope

No JavaScript is added to the Mermaid views, no automatic semantic migration
of natural-language records, and no scheduler or watchdog is added to rtmpl.
Pause captures context for the next session; it does not checkpoint running
experiments, which still belong to the tracker and results store.

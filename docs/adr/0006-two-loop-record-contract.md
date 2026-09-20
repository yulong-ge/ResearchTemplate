# ADR-0006: Two-loop research record contract

- Status: Accepted
- Date: 2026-09-20

## Decision

The BatchCom template adopts a compact `research-state.yaml` index, a single
human entry at `to_human/latest.md`, and separate project-owned homes for
hypotheses, findings, claims, decisions, experiment records, and chronology.
The state file stores IDs and relationships; it does not duplicate the
natural-language records.

Inner Loop and Outer Loop are research rhythms represented in
`research-log.md`. Each loop can be `auto` or `human`, with defaults in
`research/policy.yaml` and finite overrides in `decisions.md`. rtmpl does not
schedule experiments or infer scientific decisions.

## Consequences

- An agent can resume from three small files without reconstructing the whole
  repository.
- A human can edit the current summary and loop mode directly.
- Evolution, evidence, and trajectory views can be regenerated from the state
  and linked records.
- Applying a newer template seeds the new paths; natural-language migration is
  intentionally manual because rtmpl cannot safely infer meaning from prose.
- `.rtmpl/state.json` remains separate from `research-state.yaml` and continues
  to own template synchronization state.

## Rejected scope

No automatic semantic migration, scheduler, watchdog, or second ARA ledger is
added to rtmpl. ARA remains an opt-in artifact compilation workflow.

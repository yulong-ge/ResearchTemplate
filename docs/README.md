# Framework Documentation

This directory is for developing the copyable BatchCom research project template.

- `adr/`: architecture decisions that affect repository shape or template boundaries.
- `plans/`: implementation plans for framework changes.
- `rtmpl new` and `rtmpl init` are equivalent and print the template-defined first files to fill; `rtmpl resume` and `rtmpl check` provide the generated workspace handoff and record-contract validation.

Consumer-facing research workflow documentation belongs in `rtmpl/templates/batchcom-research/docs/`.

## When to add an ADR or a plan

Neither directory requires an entry per change; write only when the test below
applies, otherwise the code and its git history are the record.

- **ADR** (`docs/adr/`): write one when a change alters the contract that
  consumers or the sync mechanism rely on — template file boundaries, the
  research-state/policy schema, ownership policy, or a command's external
  behavior. Skip it for internal refactors and bug fixes.
- **Plan** (`docs/plans/`): write one when work spans multiple files or
  phases and needs an agreed sequence before implementation. Skip it for
  single-file or self-explanatory changes. Date-prefix plans
  `YYYY-MM-DD-<slug>.md`; delete the file once implemented rather than
  keeping it as a checklist.

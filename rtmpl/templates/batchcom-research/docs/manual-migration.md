# Manual record migration

Applying a newer template creates the new record homes and preserves project
owned records. It does not rewrite natural-language research history.

## Recommended order

1. Commit or back up the project before applying the template.
2. Run `rtmpl update --dry-run`, then apply the update with the normal project
   workflow.
3. Move the meaning by hand, keeping existing H/E/R/F/C/D IDs whenever they
   still describe the same object.
4. Split the old overview into `research-state.yaml` and
   `to_human/latest.md`; keep the state file as an index and put prose in the
   owning record.
5. Move hypothesis prose to `hypotheses.md`, chronology to `research-log.md`,
   and synthesis, claims, and decisions to their new root files.
6. Add only relationships supported by the old record. Use `unknown` when the
   historical link cannot be established.
7. Run `rtmpl check` and `rtmpl resume` before deleting the old paths.
8. Delete obsolete paths only after checking that their content has a new
   home, then run `rtmpl update` once more so their old seed state is pruned.

The migration is a human or Agent reading task. The template tool should not
guess how a natural-language observation maps to a finding, claim, or decision.

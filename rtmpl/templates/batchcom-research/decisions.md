# Decisions and authorizations

<!-- D is the home for direction decisions and finite experiment grants. A
     loop may run automatically only inside an approved, finite scope. -->

## D<id>: <decision title>

```yaml
id: D<id>
status: candidate # candidate | active | waiting | closed
approval: pending # pending | approved | rejected | superseded
decision_type: direction # direction | experiment_authorization | review | closure
decided_by: null
decided_at: null
based_on: []
supersedes: null
automation_mode: inherit_policy # manual | semi-auto | full-auto | inherit_policy
```

**Context and alternatives:** Options: A (<pros/cons>) vs B (<pros/cons>).
Fill in the real trade-off that forces this decision.

**Decision and rationale:** Decision: <choice> because <one-line reason>.

**Consequences and review trigger:**

### Experiment authorization (only for an approved batch)

```yaml
experiment_ids: []
protocol_refs: []
protocol_hashes: []
allowed_variations: []
max_runs: null
resource_budget: null
max_concurrency: null
retry_allowance: null
stop_conditions: []
expires_at: null
```

Blank or `unknown` means the scope is unspecified and must not be treated as
unlimited.

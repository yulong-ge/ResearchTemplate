# Claims

<!-- C is the only home for formal scientific claims. Findings link here and
     do not maintain a second claim-status table. -->

## C<id>: <limited-scope claim>

```yaml
id: C<id>
revision: 1
status: candidate # candidate | active | waiting | closed
evidence_status: tentative # tentative | supported_within_scope | weakened | retracted | superseded
hypothesis_refs: []
evidence_for: [] # experiment labels, R ids, or F ids
evidence_against: [] # experiment labels, R ids, or F ids
human_review: pending # pending | reviewed
supersedes: null
```

**Statement:** Keep performance, mechanism, and novelty as separate claims.
Fill in: "Claim: <statement>. Scope: <limits>. Evidence: <refs>. Weakened if: <conditions>."

**Scope:** Models, data, protocol, budget, metric, and conditions covered and excluded.

**Interpretation:** Separate direct observations from explanations.

**Alternative explanations:**

**Weakening criteria:** What evidence would downgrade or retract this claim?

**Revision history:** Preserve previous wording and the reason for each change.

# <YYYY-MM-DD> <slug>

<!--
  One significant experiment. Mirror the scientific method:
  hypothesis -> prediction -> method -> results -> interpretation.

  NOT for throwaway/exploratory runs (those are a one-liner in log.md).
  Immutable historical snapshot — if the hypothesis later evolves, do NOT
  rewrite this record; it captured what the hypothesis meant at the time.

  Full metrics/curves/media go to W&B; this file holds the human narrative.
-->

## Status

CONFIRMATORY | EXPLORATORY  ;  POSITIVE | NEGATIVE | INCONCLUSIVE

## Hypothesis & Prediction (write BEFORE running)

- **Hypothesis:** <!-- H# from ideas.md — link it, do not redefine -->
- **Prediction:** <!-- the expected measurable outcome -->
- **Rationale:** <!-- why this outcome is expected -->

## Method

- **What changed:** <!-- the delta vs baseline -->
- **Config / hyperparams:** → W&B run <!-- link -->
- **Code:** git <!-- commit --> @ <!-- branch -->
- **Command:** <!-- the exact invocation -->
- **Data:** <!-- dataset/version --> @ <!-- path or DATA_CACHE staging note -->

## Results

- **Key metric(s):** <!-- headline numbers; full curves in W&B -->
- **Observations / anomalies:** <!-- anything surprising in raw output -->
- **Sanity check:** converged? baseline reproduced? data load correct? ✓/✗

## Interpretation

- **What it means:** <!-- the human-readable meaning -->
- **Confirms / rejects hypothesis?**

## Follow-ups

- **Suggests:** <!-- next step; sync to ideas.md / findings.md with links -->

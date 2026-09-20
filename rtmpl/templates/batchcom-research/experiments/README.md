# Experiments

Create one directory per defined experiment:

```text
experiments/<id>/
  protocol.md   # scientific contract and amendments
  config.yaml   # committed executable configuration
  result.md     # grouped seed/run results and validity checks
  analysis.md   # milestone conclusions and tracker references
```

The project-selected tracker and durable results store own run-level evidence; Git records the protocol and analysis milestones. A downstream project may replace this layout only through explicit project policy.

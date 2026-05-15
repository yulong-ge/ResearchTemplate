# Research Continuity

The research files are the continuity layer for this template. Keep them updated so the next session can resume cleanly.

## Ground Truth Files

| File | Purpose | Update Frequency |
|---|---|---|
| `research/state.yaml` | Machine-readable state | After every experiment and reflection |
| `research/research-log.md` | Decision timeline | After every significant action |
| `research/findings.md` | Narrative understanding | After every outer loop |
| `experiments/results/` | Raw experimental outputs | After every experiment |

## Resuming Work

When resuming a project:

1. Read `research/state.yaml`, `research/findings.md`, and `research/current-task.md`.
2. Review the latest `research/research-log.md` entries.
3. Check whether the current experiment or analysis already has outputs under `experiments/`.
4. Continue from the recorded next step instead of restarting the reasoning from scratch.

## Long Experiments

If an experiment runs longer than the current work unit:

1. Record what is running and where outputs are being written.
2. Note health checks, partial observations, and the next inspection point.
3. Do not duplicate or restart the run unless there is evidence it failed.

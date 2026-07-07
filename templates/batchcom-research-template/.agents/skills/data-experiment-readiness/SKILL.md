---
name: data-experiment-readiness
description: Use when preparing data-processing, dataset-building, evaluation, or ML training runs where dry-runs, batch readiness, output validation, or train/val/test leakage risk matter.
---

# Data Experiment Readiness

## Overview

Use this before expensive data processing or training. The core rule: a run is not ready because commands parse; it is ready only after schema, representative processing, outputs, and split safety are checked.

## Readiness Gates

Do not skip gates. If a gate fails, stop or process only the explicitly ready subset.

1. **Environment:** correct host, working directory, runtime env, imports, GPU/CPU, disk, data mount.
2. **Source sync:** in remote-local workflows, verify the remote sees current code/config.
3. **Input schema:** manifests parse; required fields are present/non-empty; representative records are valid.
4. **Dry-run depth:** exercises the same failure points as formal run, not only CLI/path parsing.
5. **Batch readiness:** for shards/batches, produce a ready/not-ready table with blocking reasons.
6. **Output safety:** output paths, overwrite policy, permissions, sample artifacts, manifest counts.
7. **Split safety:** audit train/val/test split identifiers before training.
8. **Launch observability:** stable log, heartbeat/progress, status/manifest, success/failure marker.

## Dry-Run Minimum Bar

A useful dry-run validates:

- input files readable
- schema/required fields
- representative record processing
- output directory behavior
- sample counts and skipped reasons
- whether formal run is safe

If dry-run only checks arguments or path existence, label it “path-only” and add a readiness check before formal execution.

## Batch Readiness Report

For multi-batch/sharded data, never launch all blindly. First produce a table:

| batch/shard | records | ready | blockers | action |
|---|---:|---|---|---|

Run only `ready=true` batches. Report blocked batches explicitly; do not silently drop them.

## Split Leakage Audit

Record-level random split is unsafe when samples share a source: video frames, patients/cases/studies, windows, crops, patches, augmentations, or generated variants.

Use the strongest available group key, in this order when available: patient/case/study → series/video/source file → source image → record id. Verify train/val/test group intersections are empty. Save or log group counts and record counts.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Treating path-only dry-run as approval | Add schema and representative processing checks. |
| Running all batches before readiness | Generate readiness table; run only ready subset. |
| Starting training on derived samples with record random split | Use group split and audit overlaps. |
| Quiet long job with no status | Add unbuffered logs, heartbeat, and success/failure markers. |
| Output exists but not validated | Check manifest counts, file existence, schema, and sample artifacts. |

## Handoff to Other Skills

- Remote-local sync: Git-first — both ends pull/push the Gitee origin (see `AGENTS.md`).
- SSH/tmux/log strategy: use `remote-terminal-tool-strategy`.
- Periodic monitoring into current session: use `opencode-schedule-current-session-autostop`; if unavailable, use a tmux watchdog.

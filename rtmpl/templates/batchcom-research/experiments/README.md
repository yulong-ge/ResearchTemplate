# Experiment outputs

Use a human-chosen directory for each run or batch, for example
`experiments/baseline-check/` or `experiments/2026-09-22-ablation/`.

Store the outputs requested by the Plan: logs, metrics, configurations, checkpoints, plots, and
other raw artifacts. The directory name and its contents have no required schema. The Agent may
write here only when the Plan names the directory and the expected outputs.

Keep large or canonical assets in the locations defined by `src/paths.py`; keep only useful
references and small reproducibility metadata in Git.

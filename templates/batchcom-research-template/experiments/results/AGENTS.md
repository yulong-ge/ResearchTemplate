# Experiment Results Directory

This local directory is only a pointer/index for agents. Do not store raw artifacts or manually maintained large run trees here.

Raw artifacts should be stored under the project’s configured remote or cloud output tree, usually below `RESULTS_ROOT / <hypothesis-slug> / <run-id>`. Use experiment tracking (SwanLab, W&B) as a lightweight metadata mirror; inspect the configured run/output tree directly for detailed artifacts.

Keep this directory for:
- AGENTS.md pointer (this file)
- `.gitkeep` to preserve directory structure
- Small summary tables or cross-branch comparison notes (optional)

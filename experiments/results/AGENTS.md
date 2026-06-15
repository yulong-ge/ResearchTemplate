# Experiment Results Directory

This local directory is only a pointer for agents. Do not store raw artifacts or manually maintained run indexes here.

Raw artifacts should be stored on remote/cloud storage under `RESULTS_ROOT / <hypothesis-slug> / <run-id>`. Use experiment tracking (SwanLab, W&B) as a lightweight metadata mirror; inspect the remote results tree directly for detailed artifacts.

Keep this directory for:
- AGENTS.md pointer (this file)
- `.gitkeep` to preserve directory structure
- Small summary tables or cross-branch comparison notes (optional)

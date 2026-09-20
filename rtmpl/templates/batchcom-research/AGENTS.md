# BatchCom Research Workspace

## Resume and ownership

- Read `research-state.yaml`, `findings.md`, and `to_human/latest.md` first. `to_human/latest.md` is the daily human entry; follow its links for detailed records.
- Use the global `research-record` skill for recording and reconciliation. It routes entries to this project's declared paths.
- `research-state.yaml`, `hypotheses.md`, `research-log.md`, `findings.md`, `claims.md`, `decisions.md`, `research/environment.md`, `research/policy.yaml`, and `literature/survey.md` are project-owned seed records. `rtmpl update --force` preserves them byte-for-byte.
- Use `docs/research-workflow.md` for object ownership, evidence rules, and review triggers.
- Use `docs/manual-migration.md` when a newer template introduces new record homes; migrate prose manually and run `rtmpl check` afterward.

## Research execution

- A new experiment needs a versioned `experiments/<id>/protocol.md`, committed `config.yaml`, a result summary, and an explicit D authorization before launch.
- Exploration and confirmation are separate labels. A later result cannot rewrite an exploratory protocol into a confirmatory one.
- Launch training, resource changes, metric revisions, and automatic loop jobs only within an explicit authorization naming scope, budget, and stop conditions. Inner and Outer Loop modes are configurable; neither is forced to be manual.
- Trackers and durable results under `RESULTS_ROOT` own run-level state; record milestones in the selected analysis record.
- Operational heartbeats and routine health checks stay in machine logs or tracker state. Update Markdown at scientific milestones and interpretation-changing failures.

## Paths and storage

`src/paths.py` is the single source of truth. Project values are rendered from `.rtmpl/config.yaml`; edit the source config and run the template workflow instead of hardcoding values.

- Research NFS: `SHARED_DATA_ROOT`, `SHARED_MODEL_ROOT`, `DATA_ROOT`, `MODEL_ROOT`, and `RESULTS_ROOT` are canonical.
- Local NVMe: `DATA_CACHE` and `LIB_CACHE` are disposable acceleration layers, and keep canonical copies under the declared research roots.
- System disk, `/home/batchcom`, and `/tmp` must not hold research assets, models, results, caches, or environments.

## Environment and execution

- Mac uses `uv` for environments and CPU checks. No GPU work runs locally.
- BatchCom uses conda for CUDA/torch and `uv` for the project environment. Conda environments live under `/home/dataset-local/conda/envs`.
- On BatchCom, run in tmux: `conda activate <env> && uv run python ...`.
- From Mac, use native SSH and tmux. Preflight GPU work with `nvidia-smi`, `df -h /home/dataset-local /home/dataset-assist-0/research`, and a torch CUDA check.

## Git and verification

Keep raw artifacts out of Git. Run `uv run pytest tests/` and
`uv run python -c "from src.paths import REPO_ROOT, RESULTS_ROOT; print(REPO_ROOT, RESULTS_ROOT)"` after changes.

## Skills

- `autoresearch` orchestrates authorized Bootstrap, Inner Loop, and Outer Loop execution and synthesis.
- `research-record` routes recording and resume work.
- `ara-session-manager` is an opt-in ARA epilogue for standalone ARA artifacts; project records remain under this workspace’s declared homes.
- `rigor-reviewer` reviews an existing ARA artifact; authorization stays in `decisions.md`, and claim changes follow the project record workflow.
- `ara-compiler` is an opt-in importer for building a separate ARA from supplied research material.
- `research-ideation`, `paper-retrieval`, and `paper-writing` provide stage-specific guidance.
- `grill-with-docs` may be used for a design interview and ADR when a decision still needs user resolution.

External Skills operate within this project's ownership, authorization, evidence, and stop rules.

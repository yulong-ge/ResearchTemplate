# ADR-0003: Project and shared asset roots

- Status: **Accepted**
- Date: 2026-07-11
- Supersedes: the storage-path portion of
  `docs/plans/2026-07-07-template-refactor.md`

## Context

The template already defines project data/results roots, a local data cache,
and a cross-project library cache. It does not define project-owned models or
canonical datasets/models shared by several projects.

Read-only inspection of the live `batchcom-a100` server on 2026-07-11 confirmed
three materially different storage classes:

| Mount | Current filesystem | Current allocation | Contract |
|---|---|---:|---|
| `/` | container overlay | 50 GB | instance-local and lossy; never an asset store |
| `/home/dataset-local` | local XFS/NVMe | 1.2 TB | high-performance storage; not the canonical asset root |
| `/home/dataset-assist-0/research` | NFS | 9.8 TB | canonical, cross-machine, restart-independent storage |

`external/wdno` is an imported, self-contained reference project. Its relative
`burgers/data` and `burgers/results` paths are part of its upstream execution
contract and are intentionally preserved. They are not project-owned path
dispersion and must not be forcibly redirected by this template.

External reference designs point toward a small number of roots rather than a
constant for every file type:

- [Lightning](https://lightning.ai/docs/pytorch/stable/common/checkpointing_basic.html)
  lets the trainer, logger, and checkpoint callback determine output layout.
- [MMEngine](https://mmengine.readthedocs.io/en/latest/api/generated/mmengine.runner.Runner.html)
  lets a project choose its own `work_dir`.
- [Diffusers](https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image.py)
  manages logs below its configured `output_dir`.
- [lightning-hydra-template](https://github.com/ashleve/lightning-hydra-template)
  keeps data separate while letting Hydra and Lightning create run directories.
- [huggingface_hub](https://github.com/huggingface/huggingface_hub/blob/main/docs/source/en/package_reference/environment_variables.md)
  treats Hub content as a configurable cache, not as project-owned canonical
  model storage.

## Decision

Keep the existing two-disk model and project location. Do not introduce a new
runtime, manifest, staging daemon, or directory-creation side effect.

Add only the missing data/model ownership boundaries. Keep `RESULTS_ROOT` as the
single template-level result boundary; projects, Lightning, W&B, or other tools
own run IDs and the layout beneath it.

```text
/home/dataset-assist-0/research/        # canonical NFS
├── _shared/
│   ├── data/<asset>/<version>/         # cross-project canonical datasets
│   └── models/<asset>/<revision>/      # cross-project canonical models
└── <project>/                          # existing REPO_ROOT
    ├── data/                           # project-owned canonical datasets
    ├── models/                         # project-owned reusable model assets
    └── results/                        # project/framework-managed outputs

/home/dataset-local/                    # high-performance NVMe
├── cache/                              # cross-project library/download caches
└── <project>/data/                     # staged project datasets
```

`_shared` starts with an underscore because project slugs cannot, preventing a
shared-root/project-name collision.

Do not add `RUNS_ROOT`, `run_root()`, `SCRATCH_ROOT`, or `MODEL_CACHE` without a
concrete project need. The current projects do not use those abstractions, and
run-directory policy belongs to each project or training framework.

## Placement rules

1. Project-owned canonical datasets, models, and results live on the research
   NFS; local storage is used only through the paths explicitly defined here.
2. Download caches are not canonical models. Curated models live in
   `MODEL_ROOT` or `SHARED_MODEL_ROOT` with provenance recorded in
   `research/environment.md`.
3. Project outputs go below `RESULTS_ROOT`; this template does not prescribe
   their run IDs or subdirectories.
4. Imported projects under `external/` retain upstream-required relative paths.
   Their internal assets follow the imported project's contract, not this
   template's project-owned asset layout.

## Consequences

- Shared datasets and models have one canonical home without duplicating them
  across projects.
- A project can distinguish reusable model assets from experiment results.
- Run management remains compatible with project code, Lightning, W&B, and
  other frameworks instead of being duplicated in the template.
- Existing project roots and `DATA_ROOT`, `RESULTS_ROOT`, `DATA_CACHE`, and
  `LIB_CACHE` remain compatible. New roots are additive.
- Existing imported-project layouts are unchanged.

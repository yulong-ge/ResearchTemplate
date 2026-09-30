# Environment and provenance

Record the environment information a human considers useful for reproducing this project. The
actual storage paths are resolved by `src/paths.py`.

## Storage layout

| Storage | Path | Durability | Holds |
|---|---|---|---|
| Research NFS | `/home/dataset-assist-0/research` | canonical and cross-machine | repositories, shared/project data, models, results |
| Local NVMe | `/home/dataset-local` | performance storage | staged data, caches, conda environments |
| System/container | `/`, `~`, `/tmp` | ephemeral | no research assets |

## Compute

- Platform:
- CUDA:
- GPU(s):
- Conda environment:
- Python:

## Key packages

Record versions in the project's `pyproject.toml` or lock file.

## Data and model registry

| Item | Version or split | Location | Notes |
|---|---|---|---|
| | | | |

## Reproducibility notes

Record seeds, determinism caveats, and other details that matter to a human reviewer.

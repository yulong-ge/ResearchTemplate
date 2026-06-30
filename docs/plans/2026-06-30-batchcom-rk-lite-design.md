# batchcom RK-lite Design

## Status

Accepted as the current v1 direction from brainstorming.

This design is specifically for the current batchcom supplier remote environment. It is not a general multi-remote framework design. Other remotes may need different workflows, including Mutagen-based designs, and should be handled later when they become concrete.

## Naming

Use `batchcom`, not "Batch Camp".

## Baseline Constraint

The existing template under `templates/ara-research-workspace/` is a carefully designed baseline. Future implementation should modify it incrementally.

Do not delete template files, directories, scripts, skills, OpenCode config, or workflow documents without first doing both:

1. Explain what behavior the existing artifact provides.
2. Ask for confirmation if the removal is not obviously mechanical or already explicitly approved.

In particular, older `scripts/remote_*.sh` files may be superseded by `rk` as the primary interface, but implementation must evaluate them before removing or replacing them.

## Core Direction

v1 should be Git-first and RK-lite.

GitHub is the code synchronization source of truth. The Mac and the batchcom server each keep a clone of the same project repository. Code changes move through normal Git operations: pull, edit, commit, push, pull.

`rk` should not try to solve Mac/server two-way file ownership, should not default to Mutagen, and should not replicate local Mac MCP tools onto the server.

`rk` is a small execution safety layer for research runs:

- check environment and paths
- wrap execution commands
- write run manifests
- keep logs discoverable
- record Git commit, command, environment, W&B mapping, and artifact paths
- optionally stage/collect scratch data for high-performance runs

## Agent And MCP Model

The Mac remains the primary agent workbench because it already has the useful MCP ecosystem and local credentials configured.

Use the Mac for MCP-heavy work:

- literature and paper workflows
- Zotero / alphaxiv / Paperclip style tools
- planning and synthesis
- large edits where local tooling is better

The batchcom server is the execution backend and emergency editing location:

- run training and evaluation
- inspect logs
- edit code directly when the Mac is unavailable
- commit and push changes back through Git

Do not treat server-local OpenCode/MCP parity as a v1 requirement.

## Repository Shape

The framework repository root owns `rk` development.

The copied project template should not contain `rk` source code. Project `src/` is reserved for the ML/research code created inside downstream projects.

Target shape:

```text
skills-driven-ara-template/
  AGENTS.md
  README.md
  docs/
  rk/                         # framework tool source, root-level
  templates/
    ara-research-workspace/
      AGENTS.md
      README.md
      .rk/
        project.toml          # project config template
      research/
      literature/
      experiments/
      src/                    # downstream project code only
      ...
```

If the current tree contains `templates/ara-research-workspace/src/rk/`, implementation should move or remove that only after checking the file content and confirming it is just the misplaced runtime scaffold.

## Project Layout On batchcom

The server project root is directly under the shared persistent research folder. Do not add an extra `workspace/` layer.

```text
/home/dataset-assist-0/research/<project>/
  .rk/project.toml
  AGENTS.md
  README.md
  research/
  literature/
  experiments/
  src/
  ...
```

Optional scratch root:

```text
/home/dataset-local/<project>/
  data/
  models/
  runs/<rk_run_id>/
  cache/
```

Default work happens under `/home/dataset-assist-0/research/<project>`. `/home/dataset-local/<project>` is only for explicit high-performance scratch workflows.

## Path Configuration

`.rk/project.toml` is the path source of truth.

Example:

```toml
[project]
name = "my-project"
target = "batchcom"

[paths]
canonical_root = "/home/dataset-assist-0/research/my-project"
scratch_root = "/home/dataset-local/my-project"
data_dir = "/home/dataset-assist-0/research/my-project/data"
models_dir = "/home/dataset-assist-0/research/my-project/models"
runs_dir = "/home/dataset-assist-0/research/my-project/runs"
logs_dir = "/home/dataset-assist-0/research/my-project/logs"
```

`rk run` reads `.rk/project.toml` and exports runtime variables:

```text
RK_PROJECT_ROOT
RK_DATA_DIR
RK_MODELS_DIR
RK_RUNS_DIR
RK_LOGS_DIR
RK_RUN_ID
```

For W&B, `rk` should not take over W&B run identity by default. It should set safe local paths/tags and record W&B mapping in the manifest:

```text
WANDB_DIR=<canonical runs dir>/<rk_run_id>/wandb
```

Default behavior should keep `rk_run_id` and `wandb_run_id` decoupled but strongly associated in the manifest.

## Code-Level Path Discipline

Path correctness should be enforced in three layers:

1. `AGENTS.md` states that data, logs, outputs, checkpoints, and local W&B files must go under `$RK_PROJECT_ROOT` unless explicitly using scratch.
2. `rk run` injects `RK_*` environment variables from `.rk/project.toml`.
3. Project code uses a small paths helper, for example `src/<project>/paths.py`, that reads `RK_*` variables and fails fast when required paths are missing.

This is stronger than relying on agent instructions alone.

## Git Workflow

Before editing:

```bash
git status
git pull --ff-only
```

Before a meaningful training run:

- ensure code is committed, or explicitly allow a dirty run for debugging
- record the commit hash in the run manifest
- do not store datasets, checkpoints, W&B artifacts, or large generated outputs in Git

Server-side edits are allowed, but must be committed and pushed. The Mac side should pull before continuing.

## `rk` Command Scope

v1 commands:

```text
rk doctor
rk run <launcher> [args...]
rk logs <run-id>
rk status <run-id>
rk kill <run-id>
rk stage ...
rk collect <run-id>
```

`rk run` is a transparent wrapper. It should not require a `--` separator.

Examples:

```bash
rk run python train.py --config configs/a.yaml
rk run accelerate launch train.py --config configs/a.yaml
rk run torchrun --nproc_per_node=8 train.py
rk run lightning run model fit --config configs/a.yaml
```

`rk` options should appear before `run` when needed:

```bash
rk --target batchcom run accelerate launch train.py
```

## Scratch Mode

Default mode uses canonical storage directly.

Scratch mode is explicit:

```bash
rk stage dataset imagenet
rk stage model sd-vae
rk run --scratch accelerate launch train.py
rk collect <run-id>
```

`rk run --scratch` must not silently copy large datasets or models. If required staged data is missing, it should fail fast and print the exact `rk stage ...` command to run.

`rk collect` is only needed for scratch runs. It should be optional and manually triggered by default.

## Python Guard

Python guard is a recommended enhancement, not the only enforcement mechanism.

Project config may expose:

```toml
[guard]
mode = "strict" # strict | warn | off
```

Meanings:

- `strict`: project-owned training entrypoints must run under `rk run`, otherwise fail fast.
- `warn`: print a warning when not under `rk run`, but continue.
- `off`: no guard; useful for tests, third-party scripts, and pure analysis code.

Default should be `strict` for project-owned training scripts, with escape hatches for third-party launchers and tests.

## Explicit Non-Goals For v1

Do not include these in v1:

- default Mutagen synchronization
- two-way Mac/server ownership state machine
- server-local MCP replication
- queue-system integration
- a general multi-remote abstraction
- automatic writes to SSH config or SSH MCP config

Future remotes can introduce their own designs when needed.

## Open Questions For Implementation Planning

1. Exact `rk` implementation language and package structure.
2. Whether `rk doctor` should allow dirty Git state for debug runs by default.
3. Exact run manifest schema.
4. How much of the existing remote shell script behavior should be ported into `rk` versus kept as reference material.
5. Whether template `.opencode/` should remain Mac-oriented only or include server-local notes.

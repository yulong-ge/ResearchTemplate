# Remote Profiles

This directory is reserved for target/server profiles and remote execution notes.

Target-specific facts, probes, and profile configuration belong here.

## batchcom Default

For batchcom, use Git as the synchronization source of truth and run commands through the external `rk` tool from the framework repository.

Canonical project root:

`/home/dataset-assist-0/research/<project>`

Optional scratch root:

`/home/dataset-local/<project>`

## Legacy Remote Scripts

The template still contains `scripts/remote_*.sh` from the previous remote framework. They cover target definitions, Mutagen one-way sync, conda remote environment setup, preflight checks, and SSH command wrappers.

They are retained for now as reference/fallback while `rk` is introduced. New batchcom work should prefer `rk doctor`, `rk run`, `rk logs`, `rk stage`, and `rk collect`.

Do not delete these scripts without explicit confirmation.

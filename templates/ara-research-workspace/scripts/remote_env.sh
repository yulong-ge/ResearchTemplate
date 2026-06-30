#!/usr/bin/env bash
# Source this from remote tmux sessions after cd'ing to the repo root.
# Usage: source scripts/remote_env.sh

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  echo "source this file instead of executing it: source scripts/remote_env.sh" >&2
  exit 2
fi

_difffriendly_remote_env_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$_difffriendly_remote_env_dir/remote_targets.sh"

export PROJECT_ROOT="${PROJECT_ROOT:-$(pwd)}"
target="$(resolve_remote_target_arg "${REMOTE_TARGET:-}")"
load_remote_target "$target"

export REMOTE_TARGET="$REMOTE_TARGET"
export CLOUD_ROOT="${CLOUD_ROOT:-$REMOTE_CLOUD_ROOT}"
export CONDA_BIN="${CONDA_BIN:-$REMOTE_CONDA_BIN}"
export CONDA_ENV="${CONDA_ENV:-$REMOTE_CONDA_ENV}"
export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/external:${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1

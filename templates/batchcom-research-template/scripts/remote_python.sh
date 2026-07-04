#!/usr/bin/env bash
set -euo pipefail

# Run a Python command on a remote target through its conda environment.
# Usage: scripts/remote_python.sh [target] <python-args...>

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/remote_targets.sh"

if load_remote_target "$1" >/dev/null 2>&1; then
  target="$1"
  shift
else
  target="$(resolve_remote_target_arg "")"
fi

load_remote_target "$target"

exec ssh "$REMOTE_SSH_HOST" "cd $REMOTE_PROJECT && source scripts/remote_env.sh && exec \$CONDA_BIN run -n \$CONDA_ENV python \"\$@\""

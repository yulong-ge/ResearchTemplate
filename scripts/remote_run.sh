#!/usr/bin/env bash
set -euo pipefail

# Run a command on a remote target through its conda environment.

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/remote_targets.sh"

if [[ $# -lt 1 ]]; then
  echo "Usage: scripts/remote_run.sh [target] <command>" >&2
  remote_target_usage >&2
  exit 2
fi

if load_remote_target "$1" >/dev/null 2>&1; then
  target="$1"
  shift
else
  target="$(resolve_remote_target_arg "")"
fi

load_remote_target "$target"
cuda_devices="${CUDA_VISIBLE_DEVICES:-}"

remote_script=$(cat <<REMOTE
cd $REMOTE_PROJECT
export REMOTE_TARGET='$REMOTE_TARGET'
source scripts/remote_env.sh
if [[ -n '$cuda_devices' ]]; then
  export CUDA_VISIBLE_DEVICES='$cuda_devices'
fi
conda_bin="\$CONDA_BIN"
if [[ "\$conda_bin" != */* ]]; then
  conda_bin="\$(command -v "\$conda_bin")"
fi
"\$conda_bin" run -n "\$CONDA_ENV" "\$@"
REMOTE
)

ssh "$REMOTE_SSH_HOST" "bash -s" <<< "$remote_script"

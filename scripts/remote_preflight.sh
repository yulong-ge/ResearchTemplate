#!/usr/bin/env bash
set -euo pipefail

# Runs a generic remote execution preflight:
#   - SSH reachability and hostname
#   - working directory
#   - cloud root existence
#   - conda and Python environment
#   - CUDA/GPU availability
#   - disk space

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$script_dir/remote_targets.sh"

if [[ $# -gt 1 ]]; then
  remote_target_usage >&2
  exit 2
fi

target="$(resolve_remote_target_arg "${1:-}")"
load_remote_target "$target"

ssh "$REMOTE_SSH_HOST" "bash -s" <<REMOTE
set -euo pipefail
cd $REMOTE_PROJECT
export CLOUD_ROOT='$REMOTE_CLOUD_ROOT'
export PYTHONPATH="\$PWD:\${PYTHONPATH:-}"
export PYTHONUNBUFFERED=1

conda_bin='$REMOTE_CONDA_BIN'
if [[ "\$conda_bin" != */* ]]; then
  conda_bin="\$(command -v "\$conda_bin")"
fi
if [[ ! -x "\$conda_bin" ]]; then
  printf 'missing conda runner: %s\n' "\$conda_bin" >&2
  exit 10
fi

printf 'target=%s\n' '$REMOTE_TARGET'
printf 'host=%s\n' "\$(hostname)"
printf 'project=%s\n' "\$PWD"
printf 'cloud_root=%s\n' "\$CLOUD_ROOT"
printf 'conda_bin=%s\n' "\$conda_bin"
printf 'conda_env=%s\n' '$REMOTE_CONDA_ENV'

df -h / "\$CLOUD_ROOT" 2>/dev/null || df -h /
nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader
"\$conda_bin" run -n '$REMOTE_CONDA_ENV' python -c 'import torch; print("torch=" + torch.__version__); print("cuda=" + str(torch.cuda.is_available()))'
REMOTE

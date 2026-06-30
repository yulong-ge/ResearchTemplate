#!/usr/bin/env bash
set -euo pipefail

# Starts and flushes a target-specific Mutagen project in one-way-replica mode.

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"
source "$script_dir/remote_targets.sh"

if [[ $# -gt 1 ]]; then
  remote_target_usage >&2
  exit 2
fi

target="$(resolve_remote_target_arg "${1:-}")"
load_remote_target "$target"
project_file="$repo_root/$REMOTE_MUTAGEN_FILE"

mutagen project start -f "$project_file" 2>/dev/null || true
mutagen project flush -f "$project_file"

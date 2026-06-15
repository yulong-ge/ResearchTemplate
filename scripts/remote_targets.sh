#!/usr/bin/env bash
# Centralized remote target definitions.
# Customize for your GPU servers: add a case entry per target.

load_remote_target() {
  local target="$1"
  case "$target" in
    example-server)
      REMOTE_TARGET="example-server"
      REMOTE_SSH_HOST="example-server.example.com"
      REMOTE_PROJECT='~/code/<your-project>'
      REMOTE_CONDA_ENV="py312"
      REMOTE_CONDA_BIN="/opt/miniconda3/bin/conda"
      REMOTE_CLOUD_ROOT="/mnt/nfs/<your-project>"
      REMOTE_MUTAGEN_FILE="mutagen.example.yml"
      ;;
    *)
      printf 'Unknown target: %s\n' "$target" >&2
      return 2
      ;;
  esac
}

resolve_remote_target_arg() {
  local provided="${1:-}"
  if [[ -n "$provided" ]]; then
    printf '%s\n' "$provided"
    return 0
  fi
  if [[ -n "${REMOTE_TARGET:-}" ]]; then
    printf '%s\n' "$REMOTE_TARGET"
    return 0
  fi
  printf 'remote target is required: pass a target or set REMOTE_TARGET\n' >&2
  return 2
}

remote_target_usage() {
  cat <<'USAGE'
Targets:
  example-server  ssh example-server.example.com, conda env py312
USAGE
}

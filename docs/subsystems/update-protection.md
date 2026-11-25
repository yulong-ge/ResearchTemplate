# Managed-file update protection

## Responsibilities and boundaries

The legacy updater synchronizes managed template files and `.rtmpl/` metadata. Files outside
the template tree are never managed. User edits to managed files require an
explicit update decision. Existing natural-language research files are
migrated manually after applying a newer template.

## Sources of truth and runtime paths

| Source and symbols                                                                                                                                              | Role                                          |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| [`FileState`, `classify_path`, `classify_universe`](../../rtmpl/core/classify.py)                                                                               | Local/template/baseline classification        |
| [`UpdatePlan`, `build_plan`, `plan_as_dict`, `_resolve`, `_apply`](../../rtmpl/commands/update.py)                                                              | Plan, JSON view, decisions, application       |
| [`status.run`](../../rtmpl/commands/status.py)                                                                                                                  | Read-only plan display                        |
| [`load_state`, `save_state`](../../rtmpl/core/state.py)                                                                                                         | Baseline hashes and validation                |
| [`safe_join`](../../rtmpl/core/paths.py), [`create_backup`](../../rtmpl/core/backup.py), [`lock`, `mark_pending`, `atomic_write_bytes`](../../rtmpl/core/tx.py) | Safe paths, backups, interrupted-update state |

The updater classifies paths, builds a plan, displays it, and applies it. `status` and
`update --dry-run` share the read-only plan representation. Normal updates
resolve decisions before applying writes and saving the baseline.

## State, constraints, failures, and compatibility

The updater preserves user deletions, rejects managed symlinks, and backs up
managed files before applying atomic changes. If an update leaves
`.rtmpl/.pending`, restore the latest backup before removing the marker.
Unresolved non-interactive choices fail; read the
[per-path decision lesson](../../LESSONS.md#resolve-every-non-interactive-update-decision)
before invoking them. Markdown receives no automatic semantic merge.

## Verification

Use the [acceptance commands](../code-standards.md#acceptance-criteria).
[`test_status_is_read_only_and_supports_json`, `test_update_dry_run_is_read_only`,
`test_update_accepts_only_explicit_paths`, `test_managed_symlink_is_rejected`,
`test_pending_marker_survives_commit_failure`](../../tests/test_commands.py)
cover the main boundaries.

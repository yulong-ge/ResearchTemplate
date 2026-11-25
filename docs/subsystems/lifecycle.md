# Template lifecycle

Default [new/init](../../rtmpl/commands/new.py) checks the five research paths
before creating missing directories. Each directory it creates gets a
`.gitkeep`. It prints optional Agent Maintenance instructions and creates no
template sync state. The [project README](../../README.md) describes both new
and existing project entry points.

The explicit `new --template batchcom-research` path still loads
[the manifest](../../rtmpl/core/template.py), renders its payload, and writes
`.rtmpl/config.yaml` and `.rtmpl/state.json`. [Adopt](../../rtmpl/commands/adopt.py)
baselines an existing copy of a managed template, and
[repair](../../rtmpl/commands/repair.py) rebuilds its state. See
[update protection](update-protection.md) for synchronization behavior.

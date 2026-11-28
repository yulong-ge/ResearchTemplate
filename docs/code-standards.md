# Framework code standards

Keep the framework, generated research project, and legacy BatchCom template
in their own locations. Document current command behavior in its
[subsystem reference](subsystems/README.md). Run Python checks with uv from the
framework root.

## Acceptance criteria

Run the [framework check entry point](toolchain.md) and inspect `git diff --check`.

For scaffolding changes, create a disposable project, repeat initialization,
and try an existing project with a conflicting file. For legacy sync changes,
also preview and check the conflict behavior in a disposable managed project.

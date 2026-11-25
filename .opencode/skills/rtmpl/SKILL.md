---
name: rtmpl
description: Use rtmpl to initialize the standard research directories or maintain a legacy managed project.
---

# rtmpl

Run `rtmpl new --path <project-directory>` to add the standard research
directories. If the user wants documentation and maintenance tools, follow
the Agent Maintenance instructions printed by the command.

For an existing managed project, run `rtmpl status --json` before
`rtmpl update`. Resolve non-interactive conflicts with per-path
`--accept PATH`, `--skip PATH`, or `--create-new PATH` as appropriate.

# Lessons from framework development

Read these before changing the framework. Each entry gives a rule, its reason,
and evidence from the existing documentation. Snapshot dates identify the
migration source; they do not claim a new incident or a new test run.

## Validate from the framework root

**Rule:** Run template validation from the repository root.

**Reason:** Running `uv` inside a template directory can select that template's
`pyproject.toml` instead of the framework environment.

**Evidence:** Pre-restructure `AGENTS.md`, Verification (snapshot 2026-10-27),
and the project-selection warning in the
[implementation plan](docs/plans/2026-09-22-rtmpl-human-workflow.md).

## A cache error is not a test result

**Rule:** If the default uv cache is not writable, use the existing project environment:

```bash
UV_CACHE_DIR=/private/tmp/researchtemplate-uv-cache uv run --no-sync pytest -q
```

**Reason:** A cache-permission error occurs before tests run and is not a test result.

**Evidence:** Pre-restructure `AGENTS.md`, Verification (snapshot 2026-10-27),
recorded the unwritable-cache case and this exact command.

## Keep third-party installation within its requested scope

**Rule:** When adding third-party capabilities, distinguish this framework from
generated projects. Include only the requested skill directories and their
installation guidance; do not install a tool CLI into the template repository
or copy unrelated upstream material.

**Reason:** Framework maintenance and generated-workspace capabilities have
different owners and destinations.

**Evidence:** Pre-restructure `AGENTS.md`, Template maintenance boundaries
(snapshot 2026-10-27); see the [template reference](docs/subsystems/workspace-template.md).

## Disabling an entry does not authorize deletion

**Rule:** A request to disable an `opencode.json` entry does not authorize
deleting it or unrelated configured entries.

**Reason:** Disabling one entry and deleting configuration are different changes.

**Evidence:** Pre-restructure `AGENTS.md`, Template maintenance boundaries
(snapshot 2026-10-27), explicitly names this authorization mismatch.

## Verify the source before designing a change

**Rule:** Verify referenced paths and upstream structure before designing changes.
Deleted paths and retired ADRs are not current design evidence.

**Reason:** A historical reference can describe a structure that no longer exists.

**Evidence:** Pre-restructure `AGENTS.md`, Template maintenance boundaries
(snapshot 2026-10-27); the [accepted ADR](docs/adr/0001-rtmpl-and-human-research-workflow.md)
records the removal of research-state commands and ownership contracts.

## Resolve every non-interactive update decision

**Rule:** Read the complete `rtmpl status --json` result before
`rtmpl update --no-input`. Supply `--accept PATH` or `--skip PATH` for every
changed or orphaned managed file in the same invocation. Do not infer a global
overwrite decision.

**Reason:** Unresolved paths abort the update; a decision for one path does not
authorize replacing other paths.

**Evidence:** Pre-restructure `README.md`, Non-interactive updates (snapshot
2026-10-27); [`_resolve`](rtmpl/commands/update.py) implements per-path decisions.

## 减少需要被强制的研究状态

**规则：** 按[已接受的 ADR](docs/adr/0001-rtmpl-and-human-research-workflow.md)
分离模板生命周期和人工研究协作；不要通过更复杂的 schema 或技能规则恢复研究记录约束。

**原因：** zeropaper 恰好演示了我们已经踩到的坑——多层 spec 对象 + 循环计数 + receipt 链 + halt 类型，复杂度膨胀到 agent 和人类都读不动。它用代码级强制（manifest、fail-closed、独立 reviewer）也没能救回可理解性。结论不是"加更多强制"，而是"砍掉需要被强制的东西"。

**证据：** [2026-09-21 调研的 zeropaper 分析](docs/research/2026-09-21-open-source-research-workflow-templates.md#26-zeropaper--全自治的反面教材)
保留了 OPERATOR_HANDOVER 的失败和人工恢复记录；2026-09-22 ADR 记录了本项目采用的边界。

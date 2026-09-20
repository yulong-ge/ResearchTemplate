# Research workflow

本项目采用以人为主、AI 协作执行、证据可追溯的研究流程。`AGENTS.md`、本文件和
`research/policy.yaml` 共同定义行为边界；全局 Skills 提供方法知识，但不能扩大授权。

## 唯一恢复入口

Agent 或人恢复工作时依次读取：

1. `research-state.yaml`：当前状态、对象 ID、关系和下一动作；
2. `findings.md`：跨实验综合；
3. `to_human/latest.md`：面向人的短摘要和待确认事项。

深入某个方向时，再按链接读取 `hypotheses.md`、`experiments/<id>/`、`claims.md`、
`decisions.md` 或 `literature/`。不要在多个文件重复维护同一事实。

## 信息归属

- `H` 假设只写入 `hypotheses.md`，包括预测、理由、来源和工作状态。
- `E` 实验的协议、配置和批次结果位于 `experiments/<id>/`；同一协议的多个 seed/run 归入同一个 E。
- `R` 结果在实验目录的 `result.md` 中汇总，原始指标和产物由 tracker 与 `RESULTS_ROOT` 负责。
- `F` 跨实验综合只写入 `findings.md`。
- `C` 原子主张只写入 `claims.md`，分别记录范围、正反证据、证据状态和削弱条件。
- `D` 决策和有限批次授权只写入 `decisions.md`。空白或 `unknown` 不表示无限预算。
- `research-log.md` 是 Inner/Outer Loop 的时间线；`research-state.yaml` 只保存索引和关系。
- `to_human/` 中的图和轨迹是派生视图，事实来源仍是项目记录。

## 两层循环

Inner Loop：选择 H → 写协议 → 执行 → 检查有效性 → 记录 R → 分析影响。

Outer Loop：回顾一组 E/R → 更新 F → 更新 H/C/D 关系 → 选择深化、拓展、转向或结束。

两层循环是节奏，不是额外账本。`research/policy.yaml` 的 `loop_control` 决定默认是
`auto` 还是 `human`；方向决策可以为一个有限批次覆盖默认值。Agent 只在已批准的协议、
预算和停止条件内连续执行。

研究对象统一使用 `candidate`、`active`、`waiting`、`closed`。协议执行状态和授权状态是
单独字段，不能用 `approved` 或 `running` 代替研究对象状态。

## 人工确认点

默认配置下，以下变化需要新的 D 决策或明确人工确认：研究方向、预算或资源、主要指标、
数据范围、协议实质变化、机制解释、正式科学主张和最终结论。若确实需要更高自治度，
应在 `research/policy.yaml` 和对应 D 记录中明确调整；Inner Loop 与 Outer Loop 都可以设为
自动或人工，选择记录在 `research-state.yaml` 与对应 D 记录中。

## 记录时机与证据

执行前写协议、预测、配置版本和授权。关键结果、影响解释的故障、协议变化或证据冲突
发生时写里程碑。普通健康检查、重复状态查询和无科研意义的格式调整不生成研究记录。

把观察、解释、建议和人工批准分开写。没有来源的内容写 `unknown`，不要补造时间、运行
ID、许可或文献事实。工程执行失败不能自动标记假设被反驳；有利指标也不能自动生成机制
或新颖性结论。

## ARA 与协作

ARA 是按需编译的独立工件，用于交接、审查、论文整理或外部归档，不是日常状态的第二份
账本。使用全局 `ara-compiler` 或 `ara-session-manager` 时，项目记录仍以本目录结构为准。
重要批次完成、结果矛盾、准备扩大规模、准备宣称机制或新颖性、方向转向和论文成稿前，
可建立独立审查记录；审查建议不能自动改变主张和授权状态。

应用新模板后，`rtmpl` 只负责提供新记录入口并保护已有 seed-only 内容。自然语言记录的
重组、合并和关系确认由人或 Agent 手动完成；无法确认的关系保留为 `unknown`。

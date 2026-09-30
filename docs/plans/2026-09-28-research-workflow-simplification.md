# Checklist: Research Workflow 精简与 rtmpl 完整方案

- Date: 2026-09-28
- Status: Recommended
- Scope: `~/.agents/skills/research-workflow/`、现有 ARA 技能清理、`~/.agents/skills/rtmpl/`，以及本仓库中的后续 `rtmpl` 设计
- Related decision: `docs/adr/0001-rtmpl-and-human-research-workflow.md`

## 1. 最终边界

- [ ] 全局 Research Skills 只负责文献、选题、方法和论文写作能力。
- [ ] Research Template 只负责人工 Plan、人工上下文、实验产物和人工笔记。
- [ ] `rtmpl` 只负责模板复制、变量渲染、哈希基线、更新和冲突保护。
- [ ] Research Workflow 不维护 Research Record、Hypothesis、Experiment ID、自动笔记或实验状态。
- [ ] 模板不要求 Agent 在实验前后回写 Markdown。
- [ ] `rtmpl` 不解析研究语义，也不创建研究对象。
- [ ] 不保留 autoresearch、自动实验账本或自动状态机入口。

## 2. 注册规则

只有满足以下条件的内容才保留为 `SKILL.md`：

- [ ] 用户可以直接点名使用。
- [ ] 有独立的任务边界和输出。
- [ ] 有工具、脚本或独立方法契约。
- [ ] 不只是父技能内部的背景资料、模板或长篇参考。

所有只供父技能读取的内容：

- [ ] 放入对应的 `references/` 目录。
- [ ] 使用描述性 `.md` 文件名。
- [ ] 不使用 `SKILL.md` 作为参考材料文件名，避免被 harness 递归注册。
- [ ] 更新父技能和全局引用，确保迁移后路径有效。

当前 `research-workflow` 下保留 19 个 `SKILL.md`。六个 Research Idea 技能全部保留；三个低层论文写作模板入口已经迁移为 reference Markdown 文件。

## 3. `research-workflow` 最终入口

### 总路由和四类能力路由

- [ ] 保留 `research-workflow/SKILL.md` 作为总路由。
- [ ] 总路由只选择文献、选题、方法、论文写作四类能力。
- [ ] 总路由只在任务确实跨越多个能力边界时串联多个路由。
- [ ] 保留 `paper-retrieval/SKILL.md`。
- [ ] 保留 `research-ideation/SKILL.md`。
- [ ] 保留 `ml-methodology/SKILL.md`。
- [ ] 保留 `paper-writing/SKILL.md`。
- [ ] 父级路由负责选择入口，不自动加载全部子目录内容。
- [ ] 父级路由不拥有模板工作区规则。

### 文献入口

- [ ] 保留 `paper-retrieval/alphaxiv/SKILL.md`，用于 arXiv 阅读和问答。
- [ ] 保留 `paper-retrieval/paper-search/SKILL.md`，用于多来源论文检索。
- [ ] 保留 `paper-retrieval/paperclip/SKILL.md`，用于全文和多论文材料提取。
- [ ] 保留 `paper-retrieval/papervault/SKILL.md`，用于 venue、年份和代码链接筛选。
- [ ] 让 `paper-retrieval/SKILL.md` 只保留来源选择和边界，不展开来源内部资料。

### 选题入口

- [ ] 保留 `research-ideation/brainstorming-research-ideas/SKILL.md`，用于开放式候选方向生成。
- [ ] 保留 `research-ideation/idea-spark/SKILL.md`，用于生成有文献依据和碰撞检查的候选方案。
- [ ] 保留 `research-ideation/idea-evaluator/SKILL.md`，用于审查已经写出的研究想法。
- [ ] 保留 `research-ideation/scientific-problem-selection/SKILL.md`，用于问题选择和投入风险判断。
- [ ] 保留 `research-ideation/scoop-check/SKILL.md`，用于具体新颖性主张的先验检查。
- [ ] 保留 `research-ideation/creative-thinking-for-research/SKILL.md`，因为它提供独立的创造性研究方法。
- [ ] 保留六个 Research Idea 技能的独立入口，不因入口数量较多而合并或删除。
- [ ] 让 `idea-spark` 只读取与当前研究问题相关的 pattern 文件；这里的“按需读取”是减少无关上下文，不是删除 pattern，也不是改变技能边界。
- [ ] 让 `research-ideation/SKILL.md` 继续负责在六个不同入口之间进行选择。

### 方法入口

- [ ] 保留 `ml-methodology/SKILL.md` 作为唯一方法路由入口。
- [ ] 继续将统计、训练、追踪、评测和 mechanistic interpretability 放在 `references/`。
- [ ] 只有拥有独立工具、脚本和调用契约的方法才升级为独立 `SKILL.md`。
- [ ] 删除只重复父路由内容的局部技能文件。

### 论文写作入口

- [ ] 保留 `paper-writing/ml-paper-writing/SKILL.md`，用于完整论文写作和 camera-ready 整理。
- [ ] 保留 `paper-writing/academic-peer-review/SKILL.md`，用于投稿前审稿式检查。
- [ ] 保留 `paper-writing/figure-designer/SKILL.md`，用于图的叙事、范式和布局设计。
- [ ] 暂时保留 `paper-writing/academic-plotting/SKILL.md`，用于从实验结果渲染论文图表。
- [ ] 将 `paper-writing/benchmark-paper-template/SKILL.md` 改为 `paper-writing/references/benchmark-paper-template/benchmark-paper-template.md`。
- [ ] 将 `paper-writing/intro-drafter/SKILL.md` 改为 `paper-writing/references/intro-drafter/intro-drafter.md`。
- [ ] 将 `paper-writing/tech-paper-template/SKILL.md` 改为 `paper-writing/references/tech-paper-template/tech-paper-template.md`。
- [ ] 让 `paper-writing/SKILL.md` 根据论文类型读取上述参考资料。
- [ ] 后续根据实际使用情况评估是否将 `academic-plotting` 并入 `figure-designer`。

## 4. ARA 技能清理决策

`rigor-reviewer` 原本用于 ARA（Agent-Native Research Artifact）的 Level 2 语义审查：读取 ARA 目录，检查证据与主张、论证链、探索树和实验严谨性，并生成 `level2_report.json`。

当前模板已经移除 autoresearch、Research Record、自动实验账本和 ARA 工件结构，因此这套审查器没有可供审查的目标，也不属于当前人工 Plan 工作流。

- [ ] 删除 `/Users/macbookair/.agents/skills/rigor-reviewer/`。
- [ ] 从 `research-workflow/SKILL.md` 删除 ARA 路由和 ARA 相关说明。
- [ ] 从全局技能引用、注册链接和文档中删除 `rigor-reviewer` 引用。
- [ ] 不保留兼容入口、隐藏入口或替代的 ARA 流程。
- [ ] 普通论文审稿继续使用 `academic-peer-review`。
- [ ] 当前 Research Template 不增加 ARA 目录、Level 1 校验、Level 2 报告或自动生成流程。

## 5. 参考资料布局

- [ ] 将 `research-ideation` 下的 pattern、prompt 和示例统一整理为描述性 `.md` 文件。
- [ ] 清理重复、过时或只服务旧自动化流程的研究资料，但不删除六个 Research Idea 技能各自需要的特色方法。
- [ ] 将会议模板、Bib、Sty、TeX 和 PDF 等大体积静态资料放入明确的 `references/` 子目录或独立 `paper-templates` 资源包。
- [ ] 让 `paper-writing/SKILL.md` 只保留论文类型判断、路由和选择规则。
- [ ] 检查每个 `agents/openai.yaml` 是否仍有平台特定用途；没有用途的配置随对应入口删除。
- [ ] 将 `human-note-organization.md` 从全局 Research Workflow 参考资料迁移到模板文档或 `rtmpl` 参考资料。
- [ ] 全局 Research Skills 不描述某个项目必须如何维护笔记目录。
- [ ] 模板 `AGENTS.md` 和 `docs/plans/README.md` 继续拥有人工 Plan 的工作区规则。

## 6. `rtmpl` CLI 最终设计

### 命令职责

- [ ] 只保留 `list`、`new`、`init`、`status`、`update`、`adopt`、`repair`。
- [ ] 保留 `init` 作为 `new` 的兼容别名。
- [ ] 明确 `adopt` 只建立已有项目的模板基线，不修改业务文件。
- [ ] 明确 `repair` 只修复 `.rtmpl/state.json`，不修改 `config.yaml` 或研究内容。
- [ ] 移除或重命名 `adopt --repair`，避免命令职责重叠。
- [ ] 不新增研究状态、实验记录、dashboard 或自动笔记命令。

### 更新内核

- [ ] 将更新内核拆为 `classify -> build_plan -> render_plan -> apply` 四个边界。
- [ ] 让 `status` 只读取和分类，绝不进入写入路径。
- [ ] 让 `status` 和 `update --dry-run` 共享同一个只读更新计划对象。
- [ ] 默认 `update` 只应用未修改的受管文件和新增模板文件。
- [ ] 用户编辑过的文件必须显式选择处理方式。
- [ ] 孤儿文件删除必须逐路径确认。
- [ ] 评估并移除全局覆盖式 `--force` / `--skip`，改为逐路径接受或跳过。
- [ ] `--no-input` 遇到未决冲突时失败，并列出完整待处理路径。
- [ ] 保留更新前备份、原子写入、哈希保护和 Markdown 字节级处理。

### Manifest 合约

- [ ] 校验 manifest 根节点必须是 mapping。
- [ ] 校验 `name`、`display`、`version` 的类型和格式。
- [ ] 校验变量声明、`render_files` 和模板文件真实存在。
- [ ] 校验所有 manifest 路径都是安全的相对路径。
- [ ] 校验 `exclude` 是合法 glob 列表。
- [ ] 增加 manifest schema 版本。
- [ ] 保持 manifest 只描述模板生命周期，不描述研究对象和自动化模式。

### Agent 读取接口

- [ ] 增加 `rtmpl status --json`。
- [ ] 增加 `rtmpl update --dry-run --json`。
- [x] 为 JSON 输出定义稳定字段：模板版本、路径、分类、建议动作和冲突原因。
- [ ] JSON 输出不包含研究推断、实验结论或自动生成的研究记录。
- [ ] 让 Agent 可以读取更新计划，但不能借此获得研究笔记的特殊写入权限。

### 离线行为

- [ ] 普通 `list`、`new`、`status`、`update` 不自动进行网络版本检查。
- [ ] 将版本检查改为显式操作，或删除非核心的自动检查。
- [ ] 保证网络不可用时本地模板操作仍然确定且可完成。

## 7. `rtmpl` 技能边界

- [ ] `skills/rtmpl/SKILL.md` 只保留 CLI 生命周期说明。
- [ ] 将 GitHub deploy key、BatchCom checkout 和推送流程迁移到 `batchcom-host` 或独立的代码同步技能。
- [ ] 保留 `disable-model-invocation: true`。
- [ ] 删除 `rtmpl` 技能中关于研究方法、实验解释和研究笔记维护的内容。

## 8. 验证和完成标准

- [ ] `research-workflow` 只保留推荐入口的 `SKILL.md`。
- [ ] 所有参考资料使用描述性 `.md` 文件名，不会被 harness 递归注册。
- [ ] `rigor-reviewer` 技能目录、路由和全局引用已经删除。
- [ ] 全局技能引用扫描通过。
- [ ] skill validator 通过。
- [ ] `uv run pytest` 通过。
- [ ] `uv run ruff check rtmpl tests` 通过。
- [ ] `rtmpl list` 通过。
- [ ] 在临时目录运行 `rtmpl new`，确认变量渲染和 `.rtmpl/` 元数据正确。
- [ ] 验证 `rtmpl status` 不写文件。
- [ ] 验证 `rtmpl update --dry-run` 不写文件。
- [ ] 验证用户编辑的受管文件不会被默认覆盖。
- [ ] 验证模板外的 `notes/`、`experiments/` 和代码文件不会被 `update` 触碰。
- [ ] 验证 `adopt`、`repair` 和损坏状态处理符合各自边界。
- [ ] 验证 JSON 输出可被 Agent 读取且字段稳定。
- [ ] 运行 `git diff --check`。

## 9. 本轮审查修复

- [x] 拒绝受管路径穿越符号链接，避免模板读写和备份触碰项目外文件。
- [x] 更新失败时保留 `.rtmpl/.pending`，让下一次运行继续走恢复提示。
- [x] `status` 和 `update` 在计划阶段校验已有配置值和渲染残留占位符。
- [x] Zotero 使用 `ZOTERO_LOCAL=true` 连接本机 Zotero，不声明或写入 Web API 密钥。
- [x] JSON 计划包含 schema、建议动作和冲突原因。
- [x] `status` 支持 `--allow-downgrade`。
- [x] ML methodology 和 paper-writing 的参考资料链接改为真实 Markdown 文件。
- [x] 引用扫描器只识别实际注册的 `SKILL.md`，并处理机器本地外部技能链接。
- [x] 全局技能审计接受 `disable-model-invocation`。
- [x] 清理模板代码中的旧 `research/environment.md` 引用。
- [x] 清理 benchmark/technical paper 的旧插件表述。
- [x] 备份目录使用微秒和冲突后缀，连续更新不会覆盖恢复点。
- [x] `university-coursebook` 和 `university-textbook` 移入 `personal/`，只在 Personal 机器分发。
- [x] 删除 `docs/chatgpt-overdefense-research.md`。

## 10. 目标结果

- `research-workflow` 只暴露研究能力入口，不拥有模板工作区规则。
- `references/` 中的资料不会因文件名为 `SKILL.md` 被额外注册。
- ARA 技能已经移除；普通论文审查由 `academic-peer-review` 负责。
- `rtmpl` 只处理模板生命周期，不能创建或维护研究状态。
- `status` 是纯读取操作，更新计划可以被 Agent 稳定读取。
- 模板外的人类笔记、Plans、实验产物和项目代码不受 CLI 语义管理。

# ADR-0001: rtmpl CLI 与人工主导的 Research Workflow

- Status: **Accepted**
- Date: 2026-09-22

## Decision summary

本 ADR 同时规定两个相互分离的边界：

1. `rtmpl` 是模板生命周期 CLI，只负责复制、渲染、比较和更新模板文件，不理解
   研究问题、假设、结果或结论；
2. Research Workflow 是人工主导的实验协作流程，人工提供 Plan 和上下文，Agent
   先提出执行方案，获得明确批准后才执行有限任务。

CLI 的元数据和研究内容属于两套不同的系统。`.rtmpl/` 只记录模板同步所需的信息，
不是研究状态；Research Workflow 不要求 Agent 读取或写入 `.rtmpl/`、研究账本或实验
后的 Markdown。

## Context

当前项目把模板生命周期、研究状态建模和实验执行协作放在同一个 CLI 与模板契约中。
CLI 除了复制和更新模板，还试图校验研究对象、恢复研究上下文、生成 dashboard、
维护自动化模式，并要求 Agent 在实验前后更新多份 Markdown。

这种设计有两个独立的问题：

- 模板同步确实需要机械化的文件比较、占位符渲染和用户修改保护；
- 研究问题、实验解释和笔记整理需要人的判断，不适合交给一个依赖自然语言约束的
  Agent 状态机。

如果不把两者拆开，Agent 会把 CLI 的模板元数据误认为研究状态，也会为了满足研究
记录契约主动修改没有被人工授权的文件。目标设计保留 CLI 在模板生命周期上的价值，
同时把 Research Workflow 缩减为一次人工 Plan 驱动的一次具体任务。

## Decision 1: rtmpl CLI design

### 1.1 CLI 的唯一职责

`rtmpl` 只管理以下内容：

- 从仓库内置模板创建项目；
- 渲染模板声明的变量；
- 记录模板版本和文件基线；
- 比较模板与项目文件的差异；
- 在不静默覆盖用户修改的前提下更新模板；
- 将一个已有的手工复制项目纳入模板管理。

`rtmpl` 不执行实验，不读取研究笔记来推断任务，不解释结果，不生成科学结论，也不
决定实验是否应该开始。

### 1.2 命令表面

目标命令集合如下：

| 命令 | 作用 | 是否读取研究内容 |
|---|---|---|
| `rtmpl list` | 列出内置模板 | 否 |
| `rtmpl new <name>` | 复制模板、渲染变量并初始化 CLI 元数据 | 否 |
| `rtmpl init <name>` | `new` 的兼容别名 | 否 |
| `rtmpl update` | 预览并应用模板文件更新 | 否 |
| `rtmpl status` | 只读显示模板文件差异 | 否 |
| `rtmpl adopt` | 为已有手工复制项目建立模板基线 | 否 |
| `rtmpl repair` | 修复 `.rtmpl/` 内的 CLI 元数据 | 否 |

以下能力不属于 `rtmpl` 的目标命令集合，应从 CLI 契约中移除：

- `check`、`check --consistency`：研究记录和对象关系校验；
- `resume`、`pause`：研究上下文交接；
- `doctor`：研究记录占位符和状态检查；
- `summary`、`graph`：研究 dashboard 和轨迹派生视图。

这些命令的问题不是默认模式不够保守，而是它们把科学语义放进了模板生命周期工具。

### 1.3 CLI 元数据

每个由 CLI 管理的项目最多保留以下工具元数据：

```text
.rtmpl/
├── config.yaml       # 模板名称、创建时间和渲染变量
└── state.json        # 模板版本与模板文件基线哈希
```

这两个文件只回答“模板更新会影响哪些文件”，不回答“研究现在进行到哪一步”。
Agent 不应手动编辑它们；需要修复时使用 `rtmpl repair`。

`template.yaml` 只存在于模板源中，用于声明模板名称、版本、变量、渲染文件和安全的
文件路径规则。它不声明假设、主张、实验关系、自动化模式或研究记录所有权。

### 1.4 更新与用户修改保护

`rtmpl update` 遵守以下不变量：

1. 项目中不在模板树内的文件永远不属于 CLI 的更新范围；
2. 模板文件被用户修改后，CLI 必须报告冲突并要求明确选择；
3. Markdown 不做自动的语义合并，冲突内容以独立副本或差异形式交给人处理；
4. `--dry-run` 和 `status` 不写入业务文件；
5. 非交互模式遇到未解决冲突时直接失败，不猜测覆盖策略；
6. `adopt` 和 `repair` 不修改研究代码、实验产物或人工笔记；
7. CLI 只写模板文件和 `.rtmpl/` 元数据，不因“保持一致”扩展写入范围。

哈希、临时文件、备份和原子替换属于同步实现细节，可以保护模板更新的机械不变量，
但它们不承担研究内容的语义迁移。模板删除或重命名造成的旧文件迁移由人检查和处理，
CLI 不根据文件内容猜测其科学含义。

更新计划由 `classify -> build_plan -> render_plan -> apply` 组成。`status` 只执行读取，
不创建项目锁、不写入 `.rtmpl/`，并与 `update --dry-run` 共享同一计划表示。非交互更新
通过 `--accept PATH`、`--skip PATH` 和 `--create-new PATH` 逐路径解决冲突，不提供全局
覆盖策略。`status --json` 和 `update --dry-run --json` 提供稳定的文件分类、建议动作和
冲突原因，供 Agent 读取。

`template.yaml` 使用 schema 版本并校验根节点、字段类型、变量声明、渲染文件和安全路径。
普通 CLI 命令不自动执行网络版本检查，以保持本地模板操作的确定性。

受管路径在读取、写入、删除和备份前都会检查每个已有路径组件；符号链接穿越直接失败，
因此模板操作不会借由项目内链接触碰项目外文件。更新事务只有在文件、配置和状态全部提交
成功后才清除 `.rtmpl/.pending`，失败时保留恢复标记。`status --json` 和
`update --dry-run --json` 的文件项包含 `state`、`suggested_action` 和
`conflict_reason`，供脚本稳定消费。模板若需要外部凭据，只能通过运行时环境变量提供，
不得作为 `rtmpl` 变量写入 `.rtmpl/config.yaml`。当前 Zotero 配置使用
`ZOTERO_LOCAL=true` 访问本机 Zotero，不声明 Web API key 或 library ID。

### 1.5 CLI 的非目标

`rtmpl` 不提供以下能力：

- 研究对象 ID、关系图或状态机；
- Hypothesis、Idea、Claim、Decision 等一等研究对象；
- 实验调度、资源授权、预算管理或停止条件判断；
- 读取整个项目并自动寻找“下一步”；
- 自动改写研究笔记、实验解释或论文材料；
- 通过网络获取研究上下文或替 Agent 选择文献、数据和模型。

保留 CLI 而不是退回完全手工复制，是因为占位符渲染、文件基线和更新冲突属于
机械且可测试的问题。CLI 的价值止于此边界。

## Decision 2: Research Workflow modification

### 2.1 不再建立 Agent 维护的研究对象模型

模板不再要求 Agent 维护以下一等对象或对应账本：

- Hypothesis、Idea、Finding、Claim、Decision；
- research state、对象 ID、对象关系和自动化模式；
- Inner Loop、Outer Loop、研究时间线和 dashboard；
- 实验前后的固定 Markdown 回写步骤。

人可以按自己的方法在笔记中使用这些词，但它们不再是模板 schema，也不再由 CLI 或
技能强制产生、链接、迁移或校验。

### 2.2 最小工作区

模板只保留人工上下文、执行计划和实验产物的普通目录：

```text
docs/
└── plans/
    └── YYYY-MM-DD-<short-description>.md   # 人写的任务入口

experiments/
└── <human-chosen-name>/                    # 实验输出与原始产物

notes/                                       # 随代码版本化的项目笔记（含 environment.md）
```

`experiments/` 只承担保存实验结果和运行产物的职责。实验目录不要求语义 ID、固定
的 `protocol.md`/`result.md`/`analysis.md` 三件套，也不要求在多个文件中重复实验描述。
目录名由人选择，是否重复、合并或扩展实验由人决定。

一个实验的动机、做法、执行范围、结果和结论写在同一个 Plan 文件里，不拆分为协议、配置、
结果多文件，也不使用 E-/H-/D- 之类的追溯 ID。模板文件统一使用中文。

生成项目的 `AGENTS.md` 描述「如何做这个研究项目」（研究问题、方法、指标、代码入口、协作方式），
初始化后由人按项目改写；它不描述如何使用模板。BatchCom 磁盘/缓存/conda 规则与 SSH/tmux 长任务
做法只在全局技能 `batchcom-host`、`durable-terminal` 中维护，模板仅引用技能名，避免双源。
日报、周报等个人记录放在人自己的笔记软件中，不进入项目模板；Plan 不提供固定模板，只要求写明
可改路径、输出目录、资源预算和停止条件。

### 2.3 人工 Plan 驱动一次任务

每次实验由人创建一个 Plan，并提供足够上下文。Plan 可以是普通 Markdown，不需要
额外 schema；建议包含：

- 要回答的问题和成功标准；
- 已知背景、数据、代码入口和先验信息；
- Agent 可以读取的文件；
- Agent 可以修改的文件和输出位置；
- 资源限制、命令、预算和停止条件；
- 需要人在执行前确认的选择。

Agent 的处理顺序固定为：

1. 读取人明确提供的 Plan 和上下文；
2. 在对话中给出详细执行计划、文件清单、命令、预期输出和风险；
3. 停止并等待人的明确执行指令；
4. 只在批准的文件范围内修改代码、配置或运行实验；
5. 报告原始输出、异常和观察，不自动整理成科学结论。

Agent 不主动扫描项目来寻找 Spec、假设或隐藏的下一步，也不把自己的计划自动写回
研究笔记。人可以明确要求 Agent 起草或修改 Plan，但这属于一次单独授权的文件编辑。

### 2.4 文件所有权与写入边界

| 内容 | 默认所有者 | Agent 默认行为 |
|---|---|---|
| Plan 与背景上下文 | 人 | 读取人明确提供的内容；不主动扩写或重组 |
| `notes/`、`literature/`、`paper/` | 人 | 只读；除非 Plan 明确授权具体文件 |
| 项目代码与配置 | 项目维护者 | 只修改 Plan 列出的路径 |
| `experiments/<name>/` | 人决定目录和用途 | 写入 Plan 指定的结果、日志和产物 |
| 结果解释、跨实验综合、论文结论 | 人 | 报告观察，不代写结论 |
| `.rtmpl/` | `rtmpl` CLI | 不手动编辑，不作为研究上下文 |

Agent 发现需要扩大文件范围时必须停下，说明原因并等待人更新 Plan。Subagent 只能
处理已经批准 Plan 中的独立子任务，不能自行拆解研究问题、选择研究方向或接管记录。

### 2.5 人工确认点

以下事项由人直接决定，不由 Agent 或 CLI 推断：

- 研究问题和背景范围；
- 是否执行一次实验；
- 代码、数据、模型、资源和预算范围；
- 是否接受异常结果和如何解释；
- 是否将结果写入笔记、论文或后续研究计划。

模板不再提供 `manual`、`semi-auto`、`full-auto` 等模式。一次任务是否继续，只由
当前 Plan 和人的明确指令决定。

## Decision 3: Skill registration and context boundary

Research Workflow 的技能目录也遵守“只提供当前任务需要的能力”这一边界。`SKILL.md`
只用于以下两类内容：

1. 有清晰触发条件、可以独立调用并执行一项工作的技能；
2. 有清晰用户入口、负责路由这些独立技能的精简 router。

只用于解释背景、提供写作参考或供父技能偶尔查阅的内容，不创建独立的
`SKILL.md`。这类内容放在所属技能的 `references/` 目录中，使用描述性的 `.md`
文件名；父技能只在当前任务确实需要时指向它。这样既保留可复用的知识，也避免把
每份参考材料注册成常驻技能上下文。

保留的独立技能只有在 Agent 必须自动发现它，或另一个技能必须调用它时才使用
model-invocation；只由人明确触发的技能和 router 使用 `disable-model-invocation: true`
减少常驻描述上下文。这个 frontmatter 选择与“是否保留 `SKILL.md`”分开审计，不能用
一个宽泛的技能描述代替明确触发条件。

本 ADR 同时作出以下具体决定：

- 删除 `autoresearch` 技能及其路由、文档和注册项。它不再作为默认能力、显式高级
  能力或兼容入口保留；当前人工 Plan 流程没有自治实验循环。
- 移除 `research-record` 的独立技能入口。人类笔记整理规则如果仍有保留价值，提取
  为模板内的 `docs/human-note-organization.md`，不再以
  `SKILL.md` 注册，也不参与普通实验路由。
- 对 `research-workflow/` 下其余嵌套 `SKILL.md` 做一次逐项审计。只有符合上述两类
  内容的文件继续注册；纯参考内容移动到所属 `references/`，无用内容直接删除。
- 删除为旧 ARA/autoresearch 工件流程服务的 `rigor-reviewer` 技能及其路由；普通论文审查由
  `academic-peer-review` 负责。
- 更新父级 router、技能引用、Vendored registry 和 Claude 技能链接，使注册清单与
  实际目录一致。迁移不改变仍有明确独立用途的领域技能。

## Boundary between the two decisions

两套职责按以下规则连接：

```text
人写 Plan 与提供上下文
        │
        ▼
Agent 提出执行方案并等待批准
        │
        ▼
Agent 修改授权代码 / 运行实验
        │
        ├── rtmpl：只在需要模板创建或更新时处理模板文件
        └── Research Workflow：只报告运行输出，不维护研究账本
        │
        ▼
人整理实验结果、解释证据并决定下一步
```

`rtmpl status` 的“状态”永远只表示模板文件差异；它不表示实验状态、研究方向或
科学结论。Research Workflow 即使完全不安装 `rtmpl` 也可以工作。

技能注册边界与上述两套职责相同：`rtmpl` 技能只帮助人使用模板生命周期命令，
Research Workflow router 只把明确的 Plan 任务路由到所需的执行技能；二者都不以
`autoresearch`、研究记录账本或隐藏的全库扫描作为后备路径。

## Alternatives considered

### 让 rtmpl 同时维护模板和研究状态

拒绝。模板更新是机械问题，研究解释是人工判断。把两者放进同一套状态和命令会扩大
Agent 的默认读取和写入范围，也会使模板升级承担无法可靠自动迁移的自然语言内容。

### 完全移除 CLI，所有模板操作都使用普通复制

暂不采用。占位符渲染、模板差异、用户修改保护和旧项目基线管理具有明确的机械边界，
保留一个不理解研究语义的 CLI 可以减少重复手工错误。

### 通过更复杂的 schema 或技能规则恢复研究记录约束

拒绝。复杂 schema 只能增加字段和校验路径，不能替人判断结果意义。当前需要的是缩小
Agent 的授权范围，而不是增加它要维护的研究对象。

### 让 Agent 自动生成实验后 Markdown

拒绝。原始输出可以由 Agent 报告，结果解释、异常归因和跨实验综合由人完成；模板不
把这些内容设为自动化步骤。

## Consequences

正面影响：

- `rtmpl` 仍能可靠处理模板复制和更新，但不会把 CLI 状态伪装成研究状态；
- Agent 默认只接触人工 Plan 指定的上下文和文件；
- 实验目录恢复为结果和产物容器，不再承担对象图或状态机职责；
- 人可以在实验后自由整理笔记，不需要满足模板规定的 Markdown 回写顺序；
- 机械不变量由 CLI 处理，科学判断回到人机协作边界内。

代价和风险：

- 模板更新冲突和旧项目迁移仍需要人工选择；
- 不再自动生成跨实验状态摘要、dashboard 或研究下一步；
- 如果运行环境给 Agent 整个仓库的写权限，目录约定本身不能形成操作系统级隔离；
- 旧项目中的研究记录需要人工整理，CLI 不提供自然语言语义迁移。
- 专门技能的入口数量和常驻上下文会减少；需要特殊能力时，用户必须明确触发保留的
  独立技能或由 router 指向它。
- `autoresearch` 不再可调用，旧配置不会通过别名或兼容层继续进入自治循环。
- 参考资料仍可被人工或父技能按需阅读，但不会因为文件名位于技能目录就自动注册。

## Implementation scope

接受本 ADR 后，按以下顺序实施：

1. 将 `rtmpl` 命令收敛到 `list`、`new/init`、`update`、`status`、`adopt`、`repair`，
   并移除研究语义命令及其核心校验模块。
2. 保留 `.rtmpl/config.yaml` 和 `.rtmpl/state.json` 作为 CLI 私有元数据，清理其中
   与研究对象、seed record 和研究状态相关的契约。
3. 重写模板 README、AGENTS.md、`docs/plans/README.md` 和实验说明，改为人工 Plan
   驱动的工作流。
4. 从模板移除研究状态索引、自动化策略、对象记录模板和派生 dashboard；保留普通的
   人工笔记、文献和论文目录。
5. 将实验模板收敛为人选择的目录和运行产物，不再强制实验 ID、固定记录三件套或
   Agent 的前后 Markdown 更新。
6. 对已有项目逐个进行人工迁移和运行验证；CLI 不自动推断或合并旧研究记录。
7. 审计 `~/.agents/skills/research-workflow/` 下的全部 `SKILL.md`，删除
   `autoresearch`，移除 `research-record` 的注册入口，并把纯参考内容移动到
   `references/` 下的描述性 Markdown 文件。
8. 更新父级 router、交叉引用、`VENDORED.md` 和技能链接；用注册清单验证没有孤立的
   `SKILL.md` 或指向已删除技能的引用。

## Acceptance criteria

- `rtmpl` 的命令和代码不读取研究笔记来推断任务，也不写入研究结论；
- `.rtmpl/` 只包含模板生命周期元数据，不出现研究对象、关系或自动化模式；
- `rtmpl update` 对用户修改提供明确冲突结果，不静默语义合并 Markdown；
- 新实验可以从一个人工创建的 Plan 开始，Agent 在执行前必须先给出详细方案并等待
  明确批准；
- `experiments/` 不要求语义 ID、固定记录 schema 或实验后 Markdown 回写；
- 模板没有要求 Agent 维护 Hypothesis、Idea、Finding、Claim、Decision 或 Loop 账本；
- 结果解释、跨实验综合和后续方向由人工决定；
- `docs/adr/` 只保留当前架构决策，不保留会改变上述边界的旧决策文件；
- 活动的 `research-workflow` 注册清单中不存在 `autoresearch` 或
  `research-record/SKILL.md`；
- 每个保留的 `SKILL.md` 都能对应一个明确的独立触发场景或 router 职责，参考资料不
  使用 `SKILL.md` 文件名；
- `research-workflow` 的父级 router、`VENDORED.md` 和 Claude 技能链接与实际注册
  清单一致，技能引用检查通过。

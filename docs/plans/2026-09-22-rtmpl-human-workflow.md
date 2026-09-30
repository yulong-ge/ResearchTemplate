# Implementation Plan: rtmpl CLI 与人工主导 Research Workflow

- Date: 2026-09-22
- Status: **Implemented**
- Decision: `docs/adr/0001-rtmpl-and-human-research-workflow.md`
- Scope: framework repository、copyable template，以及与模板默认行为直接相关的全局技能

## 1. Target outcome

完成后，系统分成两个互不混淆的边界：

| Boundary | Owns | Does not own |
|---|---|---|
| `rtmpl` CLI | 模板复制、变量渲染、模板基线、更新差异、冲突保护 | 研究问题、实验执行、研究状态、结果解释 |
| Research Workflow | 人工 Plan、人工提供上下文、有限执行、人工整理结果 | 自动维护账本、自动生成结论、全库扫描和实验后 Markdown 回写 |

CLI 的 `.rtmpl/config.yaml` 和 `.rtmpl/state.json` 只记录模板生命周期信息。普通实验
不需要安装或调用 `rtmpl`，也不需要创建 `research-state.yaml`、`policy.yaml`、
Hypothesis/Claim/Decision 记录或 dashboard。

## 2. Constraints and assumptions

1. 先完成代码和模板迁移，再清理全局技能中的旧指引；每个阶段都必须有可运行的验证。
2. 保留模板同步的哈希、原子写入和冲突报告能力；这些是机械不变量，不属于研究状态。
3. `init` 保留为 `new` 的兼容别名，避免无必要的命令破坏。
4. 现有 `.rtmpl/state.json` 中的旧 `ownership` 字段可以读取但不再使用，下一次写入时
   丢弃；不对研究内容做自动语义迁移。
5. 旧研究文件由人工迁移或删除。CLI 只报告模板差异，不根据文件内容猜测去留。
6. `autoresearch` 不再保留，也不提供兼容别名、显式高级入口或普通流程外的后备触发
   路径；本计划会删除其本地技能目录和注册项。其他独立工件技能是否保留，按其自身
   触发契约审查，不纳入普通实验路由。
7. 工作区当前已有与本任务无关的 `.agents` 脏改动、`docs/research/` 和其他未跟踪
   文件；实施时只修改本计划列出的路径。
8. `~/.agents/skills/research-workflow/` 下只有可独立触发的能力或精简 router 才能
   保留 `SKILL.md`；纯参考材料必须进入所属技能的 `references/` 目录，并改为描述性
   `.md` 文件名。

## 3. Phase 0 — baseline and decision lock

### Actions

1. 由人确认 ADR；确认后再将状态从 `Proposed` 改为 `Accepted`，并以本计划作为唯一实施入口。
2. 在仓库根目录运行 `uv run pytest`，记录迁移前基线。
3. 运行 `rtk git status --short`，确认本任务的写入集合与既有脏改动分离。
4. 列出需要人工迁移的现有下游项目；没有项目清单时只完成框架仓库，不猜测外部路径。

### Completion criteria

- ADR 已明确接受；
- 基线测试结果已记录；
- 外部项目迁移被列为独立 rollout，不阻塞本仓库实现。

## 4. Phase 1 — reduce the rtmpl CLI to template lifecycle

### 4.1 Command surface

保留并测试：

- `rtmpl list`
- `rtmpl new <name>` / `rtmpl init <name>`
- `rtmpl update`
- `rtmpl status`
- `rtmpl adopt`
- `rtmpl repair`

从 parser、实现和测试中移除：

- `check`、`check --consistency`
- `resume`、`pause`
- `doctor`
- `summary`、`graph`

### 4.2 Code changes

修改：

- `rtmpl/cli.py`：只注册模板生命周期命令；移除研究命令 import、参数和帮助文本；
- `rtmpl/commands/new.py`：删除“先填研究记录”和 `rtmpl check && rtmpl resume` 提示，
  只报告创建结果及模板元数据；
- `rtmpl/commands/_common.py`：删除研究记录 ownership、`seed_only` 和初始化指导的
  共享逻辑；
- `rtmpl/commands/adopt.py`、`repair.py`、`update.py`：只处理模板路径与哈希基线；
- `rtmpl/core/template.py`：移除 `InitStep`、`init_guidance` 和研究语义的
  `file_policies` 解析；保留变量、渲染和模板路径遍历；
- `rtmpl/core/state.py`：状态只保存 `template_version` 和 `hashes`；兼容读取旧状态
  中的额外 `ownership` 字段，但不再分类或写回；
- `rtmpl/core/classify.py`：删除 `SEEDONLY` 和 ownership 分支，保留普通模板文件的
  changed/orphaned/user-deleted 分类；
- `pyproject.toml`、`rtmpl/__init__.py`：按破坏性命令收敛更新版本和描述。

删除：

- `rtmpl/commands/check.py`
- `rtmpl/commands/doctor.py`
- `rtmpl/commands/graph.py`
- `rtmpl/commands/pause.py`
- `rtmpl/commands/resume.py`
- `rtmpl/commands/summary.py`
- `rtmpl/core/research.py`
- `rtmpl/core/consistency.py`

保留：`hash.py`、`render.py`、`template.py` 的非研究部分、`state.py` 的哈希状态、
`classify.py` 的文件差异分类、`backup.py`、`tx.py`、`version.py` 和 `update_check.py`。

### 4.3 CLI invariants

实现和测试以下不变量：

1. 模板外新增的 `notes/`、`experiments/`、代码和结果文件不被 `update` 触碰；
2. 模板内文件被用户修改时，默认报告冲突，不静默覆盖；
3. `--no-input` 遇到未解决冲突时失败并返回非零码；
4. `status` 与 `update --dry-run` 不写业务文件；
5. `adopt` 不修改业务文件；
6. `repair` 只重建 `.rtmpl/state.json`，不修改 `config.yaml` 或研究内容；
7. Markdown 只按字节/哈希处理，不做语义合并。

### Completion criteria

- `rtmpl --help` 只展示六类生命周期能力（`new/init` 算一个入口）；
- 代码中不再有研究状态校验、dashboard 构建或暂停恢复逻辑；
- 现有模板同步测试仍覆盖渲染、哈希、冲突、备份、原子写入和损坏状态；
- 旧 `.rtmpl/state.json` 可以被读取，重新写入后不含 `ownership`。

## 5. Phase 2 — rebuild the copyable template

### 5.1 Remove the old research ledger

从 `rtmpl/templates/batchcom-research/` 删除：

- `research-state.yaml`
- `research/policy.yaml`
- `hypotheses.md`
- `findings.md`
- `claims.md`
- `decisions.md`
- `research-log.md`
- `to_human/` 全目录
- `src/dashboard_builder.py`
- `experiments/_template/` 全目录
- `docs/manual-migration.md`
- `docs/research-workflow.md`
- `literature/survey.md`

将 `research/environment.md` 的存储、计算和 provenance 内容迁移到
`notes/environment.md`；只移动内容，不让 CLI 或 Agent 自动更新它。

这些路径的删除不触发语义迁移。已有项目中的有价值内容由人先移动到普通笔记、Plan、
论文或结果目录，再运行模板更新。

### 5.2 Add the minimal human workflow

新增或重写：

- `notes/README.md`：说明该目录由人维护，Agent 只读取 Plan 明确提供的文件；
- `notes/environment.md`：保留人工维护的存储、环境和 provenance 说明；
- `docs/plans/README.md`：说明实验入口 Plan 的命名、建议内容和人工批准步骤；
- `experiments/README.md`：说明此目录只保存结果、日志、配置和其他产物，不要求语义
  ID、固定文件集合或实验后 Markdown；
- `AGENTS.md`：只保留 Plan 驱动的读取/写入边界、环境执行规则和停止条件；
- `README.md`：面向人说明目录结构、如何创建 Plan、如何授权 Agent 和如何整理结果。

目标最小树：

```text
docs/plans/<date>-<description>.md   # 人写的任务入口
experiments/<human-name>/            # 实验结果和原始产物
notes/
├── environment.md                   # 可选的人类环境/provenance 记录
└── ...                              # 其他人类研究笔记
literature/notes/                    # 可选文献笔记
paper/                               # 论文材料
```

`src/paths.py`、`external/`、`.opencode/`、项目环境与存储约定继续保留；它们不属于
Research Workflow 状态机。

### 5.3 Simplify the manifest

修改 `rtmpl/templates/batchcom-research/template.yaml`：

- 保留项目名和 conda 环境渲染；Zotero 通过 `.opencode/opencode.json` 使用本地模式，
  不作为 `rtmpl` 变量渲染；
- 删除 `init_guidance`；
- 删除 `file_policies.seed_only` 与 `file_policies.generated`；
- 只保留模板文件遍历和渲染需要的字段；
- 不把 `notes/`、`experiments/` 或研究结果声明为 CLI 特殊对象。

调整 `.gitignore`，移除 dashboard、暂停上下文和研究状态生成物的专用规则。

### Completion criteria

- disposable scaffold 中不存在旧研究状态文件、dashboard 或固定实验模板；
- scaffold 包含 `notes/`、`docs/plans/` 和 `experiments/` 的最小说明；
- Agent 只看到人工 Plan 驱动的正向工作流，不被要求扫描或更新研究账本；
- `template.yaml` 不含 `seed_only`、`init_guidance` 或自动化模式。

## 6. Phase 3 — migrate tests and framework documentation

### Tests

删除旧研究状态测试：

- `tests/test_research_commands.py`

重写 `tests/test_template_research_records.py` 为 `tests/test_template_workflow.py`，验证：

- 新模板目录存在；
- 旧 ledger、dashboard 和 `_template` 路径不存在；
- 模板不复制全局技能；
- manifest 没有研究状态字段；
- 实验目录不要求特定 ID 或三件套。

调整 `tests/test_commands.py`：

- 删除 seed-only ownership 测试；
- 删除初始化时研究记录指导的断言；
- 增加 CLI 帮助只包含生命周期命令的断言；
- 保留并强化用户修改冲突、`--no-input`、adopt、repair 和 dry-run 测试。

调整 `tests/test_core.py`：

- 删除 file-policy/ownership 专用断言；
- 保留 hash、render、path-key、state health、classifier 和 version skew 覆盖；
- 增加旧 state 含额外 `ownership` 字段时的读取/清理测试。

### Framework docs

修改：

- `README.md`：只展示 `list/new/status/update/adopt/repair` 和人工 Plan 流程；
- `AGENTS.md`：删除 research-state、seed-only、Inner/Outer Loop 和旧验证命令；
- `docs/README.md`：将计划说明改为当前 CLI 与人工 Workflow 契约。

审计并清理已经被新 ADR 取代的计划内容；仍然有效的环境、存储或 Git 约定先迁移到
当前文档，再删除过时文件：

- `docs/plans/2026-07-07-template-refactor.md`
- `docs/plans/2026-09-20-adhd-optimizations.md`

保留 `docs/research/` 调研材料作为背景资料，但不把它作为 Agent 的运行时契约。

### Completion criteria

在活动代码、模板和框架文档中，以下关键词只允许出现在迁移说明或明确的历史背景中，
不得再作为默认行为：`research-state.yaml`、`automation_mode`、`Inner Loop`、
`Outer Loop`、`rtmpl check`、`rtmpl resume`、`rtmpl pause`、`rtmpl doctor`、
`rtmpl summary`、`rtmpl graph`。

## 7. Phase 4 — reduce and align global skills

这些文件位于独立的 `~/.agents` Git 仓库，实施时只修改本计划列出的路径，并保留该
仓库当前的无关脏改动。

### 7.1 Inventory before mutation

先列出 `skills/research-workflow/` 下全部 `SKILL.md`，为每个文件记录：独立触发词、
是否被父级 router 或其他技能引用、是否包含可执行步骤、是否只是背景/模板/参考。
按以下规则分类：

- **Keep**：有明确独立触发场景的 model/user-invoked skill，或承担明确用户入口的
  router，继续使用 `SKILL.md`；若不需要 Agent 自动发现，则设置
  `disable-model-invocation: true`；
- **Move**：只供查阅、解释背景或承载可复用静态材料的文件，移动到所属技能的
  `references/<descriptive-name>.md`，并从注册清单移除；
- **Delete**：与当前人工 Plan 流程无关且没有有效引用的内容，直接删除。

先完成这张清单，再执行移动和删除，避免因为目录名称或旧链接误判独立能力。最终
清单必须能由 `rg --files skills/research-workflow -g 'SKILL.md'` 重建，并与
`VENDORED.md` 和各级 router 一致。

审计结果（2026-09-23）：原有 40 个注册入口中，38 个属于可独立触发能力或 router
并保留；`research-record/SKILL.md` 的人工整理内容移动到一个普通 reference 文件；
`autoresearch/SKILL.md` 及其目录直接删除。其余技能已经把长篇静态材料放在各自的
`references/` 目录，没有发现需要继续脱离注册的 reference-only `SKILL.md`。

### 7.2 Concrete changes

1. `skills/rtmpl/SKILL.md`
   - 更新命令集合和 `.rtmpl/` 元数据说明；
   - 删除 research-state、seed-only、resume/check/doctor/graph 等默认指引；
   - 将 `status` 明确定义为模板差异，不是研究状态。
2. `skills/research-workflow/SKILL.md`
   - 保持为精简 router，只把人工 Plan 和明确批准的领域任务路由到保留技能；
   - 删除研究记录、自治循环和主动全库扫描作为普通路径的提示；
   - 保留的独立工件技能只有在其自身触发契约明确时才出现在 router 中。
3. `skills/research-workflow/autoresearch/`
   - 删除整个技能目录、所有父级路由和交叉引用；
   - 从 `VENDORED.md` 移除对应注册项；
   - 扫描实际注册目录，确认没有别名或隐藏兼容入口。
4. `skills/research-workflow/research-record/`
   - 删除 `SKILL.md` 注册入口，不再把研究记录整理作为默认可调用技能；
   - 将仍需保留的人工笔记整理说明提取到
     `rtmpl/templates/batchcom-research/docs/human-note-organization.md`；
   - 更新所有父级链接，确保参考文件不会被当成技能加载。
5. 对 7.1 中标为 **Move** 的其他内容，按所属技能分别放入其
   `references/` 目录并改名；对 **Keep** 项保留最小可执行正文，删除重复背景和不
   可触发的长篇说明。

技能变更完成后运行：

```bash
uv run --with pyyaml python /Users/macbookair/.agents/skills/skill-lifecycle/scripts/quick_validate.py /Users/macbookair/.agents/skills/rtmpl
uv run --with pyyaml python /Users/macbookair/.agents/skills/skill-lifecycle/scripts/quick_validate.py /Users/macbookair/.agents/skills/research-workflow
uv run python /Users/macbookair/.agents/skills/skill-lifecycle/scripts/check-skill-refs.py --root /Users/macbookair/.agents/skills
/Users/macbookair/.agents/scripts/sync-skill-links.sh
rg --files /Users/macbookair/.agents/skills/research-workflow -g 'SKILL.md'
if rg -n "autoresearch|research-record" /Users/macbookair/.agents/skills --glob 'SKILL.md' --glob 'VENDORED.md'; then exit 1; fi
test ! -e /Users/macbookair/.agents/skills/research-workflow/autoresearch
test ! -e /Users/macbookair/.agents/skills/research-workflow/research-record/SKILL.md
```

验证时不对移动后的 `references/*.md` 运行 skill frontmatter 校验；只验证保留的
`SKILL.md` 及其引用。技能仓库使用独立的 `agent-skills-repo-sync` 流程：只 stage
本任务明确变更的路径，提交前报告无关脏改动，并在需要提交/推送时单独取得确认。

## 8. Phase 5 — verification and migration

### Repository verification

按顺序执行：

1. `uv run pytest`；
2. `uv run rtmpl list`；
3. 用临时目录运行 `uv run rtmpl new demo --var conda_env=ml --no-input`；
4. 在 scaffold 中从框架仓库运行
   `uv run --project /Users/macbookair/code/ResearchTemplate rtmpl status` 和
   `uv run --project /Users/macbookair/code/ResearchTemplate rtmpl update --dry-run`，避免
   调用环境中旧版的全局 CLI；
5. 在 scaffold 外新增 `notes/context.md` 和 `experiments/test-run/result.json`，确认
   CLI 不将它们列为模板更新对象；
6. 修改一个模板管理文件，确认 `status` 报告 changed，非交互 `update` 在没有选择时
   失败；
7. 损坏或删除 `.rtmpl/state.json`，确认 `repair` 只修复 CLI 元数据；
8. `rtk rg` 扫描活动代码、模板和文档，确认没有旧命令和研究状态契约残留。

### Implementation result (2026-09-28)

- `uv run pytest`：47 个测试通过；`uv run ruff check rtmpl tests`：通过；
- disposable scaffold 成功生成当前模板文件，`status`、`status --json`、`update --dry-run`、
  `update --dry-run --json` 和 `repair`
  均通过；额外的 `notes/context.md` 与 `experiments/test-run/result.json` 不进入模板
  更新范围；重建后的 `.rtmpl/state.json` 不含旧 `ownership` 字段；
- `rtmpl` 与 `research-workflow` 技能校验、目标表面扫描和链接同步通过；`autoresearch`
  与 `research-record` 注册入口已移除，人工笔记说明已迁移到模板的 `docs/human-note-organization.md`；三个低层论文写作入口已迁移到
  `paper-writing/references/`；ARA 技能及其路由已删除；
  仓库级引用扫描中的本地断链和 vendor 目录排除路径已修复，扫描结果为零问题；
- 技能校验器已接受平台支持的 `disable-model-invocation` frontmatter 字段，并同步更新
  技能创建参考文档；`rtmpl` 保留该字段以维持人工触发边界；
- 本仓库没有已登记的下游项目，因此外部项目迁移保持为后续逐项目人工 rollout，不计入
  本次框架实现完成条件。

### Existing-project migration

对每个明确列出的下游项目逐个执行：

1. 先提交或备份当前工作树；
2. 人工把需要保留的研究文字移到 `notes/`、`docs/plans/`、`literature/`、`paper/`；
3. 保留实验结果和原始产物，删除或归档旧状态文件前由人确认；
4. 运行 `rtmpl status`，逐个处理旧模板路径的 orphan/conflict；
5. 运行 `rtmpl update --skip <path>` 或对具体文件作明确选择，不使用无审查的全量覆盖；
6. 运行项目自己的测试/实验检查，并由人确认迁移后的目录和结果。

### Final completion criteria

- 仓库测试和 disposable scaffold 验证通过；
- CLI 只处理模板生命周期；
- 新模板没有 Agent 维护的研究账本；
- 普通实验只需人工 Plan、明确批准和结果产物；
- 全局默认路由不再要求实验前后写 Markdown；
- `autoresearch` 已从全局技能注册和模板路由移除；
- `research-workflow` 下只有明确可调用的技能保留 `SKILL.md`，参考资料不再占用技能
  注册上下文；
- 每个下游项目的迁移结果有人工确认记录。

## 9. Commit boundaries

保持小而可回滚的提交：

1. `refactor(cli): separate template lifecycle from research workflow`
2. `refactor(template): adopt human plan workflow`
3. `docs: align framework guidance with the new contract`
4. 在 `~/.agents` 仓库单独提交 `Update rtmpl and research workflow skills`

每个提交前运行与其范围匹配的测试；不得把 `.agents` 的既有修改或本仓库其他未跟踪
调研文件混入提交。

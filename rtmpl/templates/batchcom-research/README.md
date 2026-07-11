# BatchCom 研究模板 — 研究记录指南（给人类）

本模板把研究记录组织成一组**职责不重叠**的 markdown 文件。科研会产生很多种信息，分散存放会丢失、重复存放会过期并误导。本指南回答两个问题：

1. 一个科研项目到底会产生哪些类别的信息？
2. 每一类该写进哪个文件？——以及哪个文件**绝不**该写它。

> 给 agent 的等价指引见 `.agents/skills/research-record`；本文件是给**人**的设计说明。

---

## 一、科研项目产生的信息维度

下表归纳一个完整科研项目会产生的全部信息类别（A–K），按生命周期分组。对照检查你的项目是否每一类都有归宿。

| 维度 | 具体内容 | 生命周期 |
|---|---|---|
| **A. 定位** | 研究问题、动机、当前方向、成功标准、硬约束 | 稳定（罕变） |
| **B. 构思** | 候选假设（带预测 + 理由）、想法积压 | 累积 |
| **C. 规划** | 实验设计/协议（测什么、怎么测、预期结果）、配置/超参 | 每次实验前 |
| **D. 执行** | 跑了什么/何时/命令、指标曲线、原始观察、异常、失败调试 | 每次 run |
| **E. 解释** | 单次结果含义、跨 run 规律、成熟结论、否定性结果/排除路径 | 周期性综合 |
| **F. 不确定性** | 科学未解问题、方法学疑点 | 持续 |
| **G. 决策协调** | 已做决策（含理由）、待决策、下一步、阻塞、todo | 每会话 |
| **H. 时间线** | "今天做了什么"按序记录 | 追加 |
| **I. 溯源** | 环境（conda/CUDA/GPU）、包版本、数据/模型版本、种子、路径 | 稳定 + 按变更 |
| **J. 资源** | 文献笔记、数据/模型注册表、外部链接 | 累积 |
| **K. 交流** | 报告、演示、论文草稿 | 后期 |

> **数字/曲线/media 不在此表** —— 它们进 W&B，不进 markdown。大体积原始 artifact（checkpoint 等）进入 `RESULTS_ROOT`（gitignored），不进 Git、也不进 W&B。

物理资产同样遵守“每个事实只有一个家”：跨项目复用的数据和模型分别进入
`SHARED_DATA_ROOT`、`SHARED_MODEL_ROOT`；项目独有的数据和可复用模型分别进入
`DATA_ROOT`、`MODEL_ROOT`；项目结果进入 `RESULTS_ROOT`。`DATA_CACHE` 和
`LIB_CACHE` 位于本机高速盘，不作为 canonical asset root。

## 二、维度 → 文件 速查

把上面的维度直接对到文件，一眼看清"这类信息写哪里"：

| 维度 | 写进 | 备注 |
|---|---|---|
| A 定位 | `research/overview.md` | 成功标准/硬约束也在此 |
| B 构思 | `research/ideas.md` | 假设定义的唯一归属 |
| C 规划 + D 执行 + E（单次解释） | `research/runs/<slug>.md` | 一次重要实验一篇 |
| E（跨 run 综合） + F | `research/findings.md` | 只放成熟结论与未决科学问题 |
| G（已做决策） | `research/decisions.md` | 含理由 + 备选 |
| G（待决策/下一步/阻塞/todo） | `research/overview.md` | 活状态 |
| H 时间线 | `research/log.md` | 一行 + 链接 |
| I 溯源 | `research/environment.md` | 配合 `src/paths.py` |
| J 资源（文献） | `literature/survey.md` + 单篇笔记 | |
| J 资源（数据/模型注册表） | `research/environment.md` | 与溯源同处 |
| K 交流 | `paper/` | 写作阶段 |

## 三、每个文件的职责边界

**关键原则：每个事实只有一个家。** 其他文件只放**链接**，不放内容副本——否则一处更新、另一处残留旧值，会误导自己和 agent。

| 文件 | 只装什么 | 不装什么（去这里） |
|---|---|---|
| `research/overview.md` | 当前状态、活跃方向、下一步、阻塞、待人决策、成功标准、硬约束 | 历史流水 → `log.md`；成熟结论 → `findings.md` |
| `research/log.md` | 时间线条目（一行 + 可选短链接）；可含简短 run 摘要 | 完整 run 记录 → `runs/` |
| `research/ideas.md` | 假设（带预测 + 理由）、候选/搁置/拒绝想法 | 已验证结论 → `findings.md` |
| `research/findings.md` | 成熟科学结论、跨 run 规律、解释约束、排除路径、**未决科学问题** | 工程坑 → `environment.md`/`log.md`；流水账 → `log.md` |
| `research/decisions.md` | 决策 + 理由 + 考虑过的备选（ADR 风格，按主题可检索） | 时间线 → `log.md` |
| `research/environment.md` | conda env、CUDA/GPU、包版本、数据/模型版本、种子、路径注册表（人类描述） | 代码解析逻辑 → `src/paths.py` |
| `research/runs/<slug>.md` | 单次实验全记录（假设→预测→方法→结果→解释） | 跨 run 综合 → `findings.md` |
| `literature/survey.md` | 文献综述汇总 + 单篇笔记链接 | |
| `paper/` | 手稿资产（写作阶段） | 与研究状态隔离 |

## 四、让记录不腐烂的两条习惯

1. **不是每次 run 都建 `runs/` 文件。** 探索性/抛弃型 run（跑别人代码、调 bug、随手试）只在 `log.md` 写一行；只有**重要实验**（测某个假设 / 产出可引用结果 / 出现意外）才开 `runs/<slug>.md`。事后发现某次探索很重要 → 补写 `runs/` 并把 `log.md` 那行改成链接。
2. **指针，不是副本。** 写新信息时只写进它的"家文件"；索引文件（`overview.md`、`log.md`）只放一行摘要 + 链接。读取时：`overview.md` 可整读（保持精简），其余一律按需 grep 或读末尾，不要整份读入。

完整纪律（含读取策略、W&B 边界、ctx_memory 定位）见 `.agents/skills/research-record/SKILL.md`。

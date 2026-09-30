# 开源科研工作流模板调研：人机协同边界与约束机制

> 调研日期：2026-09-21。对象：GitHub 上 12 个有代表性的研究/数据科学/Agent 协作模板与工具，全部读过一级来源（README、核心脚本、文件树、官方文档）。动机：当前 ResearchTemplate 用自然语言约束 Agent 行为，导致可编辑边界不清、概念过多（Hypothesis/Idea/Experiment/Claim/Decision）、Inner/Outer Loop 超出模型执行力、缺少代码级强制。目标是回到"人工写 Plan → Agent 详化 → Agent 执行"的人机协同模式。

## 0. 结论先行

1. **几乎所有成功模板都不给 Agent 一个"研究状态机"**。它们要么根本不建模科学概念（CCDS、ML 模板只管目录和 config），要么只建模一个对象——**任务**（Backlog.md、OpenSpec、spec-kit）——把"假设/发现/决策"全部压成任务文件里的一段文字。我们模板里 6 个一等公民概念（hypothesis/finding/claim/decision/experiment/log）在开源世界没有先例；最接近科学概念建模的 science-superpowers 也只保留**一个**对象：pre-registration。

2. **约束靠的是工具，不是文字**。三种被验证有效的强制手段，按成本从低到高：
   - **git commit 即时间戳**（science-superpowers 的 `prereg.sh`）：freeze 一次提交，`audit` 子命令能从 git 历史证明"预测先于结果、文件未被事后修改"——把"先看数据再注册"从自然语言禁令变成可验证的 exit code。
   - **CLI 生成和校验记录文件**（Backlog.md、spec-kit、rtmpl 已有的 `check`）：Agent 不手写 YAML frontmatter，而是跑 `backlog task create --ac "..."`，ID、日期、依赖关系由 CLI 保证合法。自然语言只写描述段，机器可校验字段全部交给工具。
   - **目录即权限边界**（CCDS 的 `data/raw/` 不可变约定、zeropaper 的 fail-closed manifest）：与其告诉 Agent"哪些文件不能改"，不如把不可改的东西放进单独目录，用 `.gitignore`/CI check/`rtmpl check` 守住，而不是靠 AGENTS.md 里的禁令段落。

3. **人机分工的稳定模式是"三道审查门"**，来自 Backlog.md（6.8k stars，自己 dogfooding）和 spec-kit（138k stars）：
   - 人审 **spec/plan**（agent 写的，一行字能驳回，比重写便宜）
   - 人审 **实施计划**（agent 调研后写进任务，批准才动代码）
   - 人审 **产物**（一个任务一个 PR，diff 控制在人能读完的规模）

   这恰好就是我们要的"人工 Plan → Agent 详化 → Agent 执行"，社区已经把它做成了标准循环。

4. **全自治是最差对照组，不是目标**。zeropaper（自动论文管线）的 OPERATOR_HANDOVER 是现成反面教材：一条管线跑了 32 版 spec、6 次 build failure 超 cap、15 次尝试 13 次没拿到 verified receipt，最后靠人类 operator 手工 halt 并写交接文档。它自己的人机边界（operator 盯 driver.log、手工 flip `status` 回 `running`、授权范围写进 commit message）反而证明：**就算作者全力做全自治，收口的仍是一个人读状态文件做判断**。

---

## 1. 调研对象总览

| 项目 | Stars | 类型 | 与我们的相关性 |
|---|---|---|---|
| [drivendataorg/cookiecutter-data-science](https://github.com/drivendataorg/cookiecutter-data-science) | 10.1k | 数据科学目录模板 | 目录约定与不可变区的基准 |
| [github/spec-kit](https://github.com/spec-kit/spec-kit) | 138k | Spec 驱动开发工具包 | Specify→Plan→Tasks→Implement 门控 |
| [Companion-Inc/feynman](https://github.com/Companion-Inc/feynman) | 9.7k | AI 研究 agent | 有界实验循环的最小记录形态 |
| [MrLesk/Backlog.md](https://github.com/MrLesk/Backlog.md) | 6.8k | Markdown 任务账本 | 人机三道审查门的最佳样板 |
| [Fission-AI/OpenSpec](https://github.com/Fission-AI/OpenSpec) | 69.7k | Spec 驱动开发 | change/proposal/tasks 的增量模型 |
| [K-Dense-AI/science-superpowers](https://github.com/K-Dense-AI/science-superpowers) | 336 | 科学方法论技能包 | pre-registration + git 时间戳审计 |
| [buoyancy99/research-template](https://github.com/buoyancy99/research-template) | 165 | ML 实验模板（MIT 博士生） | hydra 组合式实验，无研究状态 |
| [CLAIRE-Labo/python-ml-research-template](https://github.com/CLAIRE-Labo/python-ml-research-template) | 121 | ML 模板（EPFL 实验室） | 可复现性工程做到极致，零概念建模 |
| [mila-iqia/ResearchTemplate](https://github.com/mila-iqia/ResearchTemplate) | 54 | ML 模板（Mila） | copier 模板 + hydra，同构 |
| [konstantinjdobler/nlp-research-template](https://github.com/konstantinjdobler/nlp-research-template) | 10 | NLP 模板 | conda-lock/Docker 环境冻结 |
| [alejandroll10/zeropaper](https://github.com/alejandroll10/zeropaper) | 72 | 全自治论文管线 | 反例：过度自动化的实际代价 |
| [elabftw/elabftw](https://github.com/elabftw/elabftw) | 1.4k | 电子实验记录本（ELN） | 不可变记录 + trusted timestamping |
| [benmarwick/rrtools](https://github.com/benmarwick/rrtools) | 720 | R 可复现研究包 | analysis/ 单目录收纳产出物 |

---

## 2. 逐项目分析

### 2.1 Cookiecutter Data Science（CCDS）——"目录即边界"的鼻祖

**基本信息**：DrivenData 维护，10.1k stars，数据科学项目结构的事实标准，v2 用 `ccds` CLI 生成。

**结构**：

```
├── Makefile            # make data / make train 之类的入口
├── data/
│   ├── external/       # 第三方数据
│   ├── interim/        # 中间产物
│   ├── processed/      # 最终数据集
│   └── raw/            # 原始数据，不可变
├── docs/  models/  notebooks/  references/  reports/
└── <module>/           # 可安装的 Python 包
    ├── config.py  dataset.py  features.py
    ├── modeling/{train,predict}.py
    └── plots.py
```

**核心设计**：它的 opinions 文档只有一条硬规则——**"数据分析是 DAG，raw data 不可变"**。没有 hypothesis/experiment 对象，没有状态文件，没有自动化模式。约束力来自两处：`data/` 整体进 `.gitignore`（数据不进版本控制是默认行为），以及 `raw/` 目录的命名约定 + 文档里反复的 "Don't ever edit your raw data"。

**人机边界**：全部工作由人做；模板只管"东西放哪"。自动化只有 Makefile 入口命令。

**对我们的启发**：CCDS 证明**单靠目录语义就能撑住十年的协作**——`raw/` 不可变不需要状态机，只需要一个目录名和一条团队约定。对应到我们：`research-state.yaml`、dashboard 这类"agent 生成物"应该和"人类手写的 plan/notes"在物理上分开目录，边界用路径前缀表达，而不是在 AGENTS.md 里枚举文件名清单。

---

### 2.2 ML 实验模板四家：buoyancy99 / CLAIRE-Labo / Mila / nlp-research-template

**基本信息**：四家合计约 360 stars，分别来自 MIT 博士生、EPFL CLAIRE 实验室（ML Reproducibility Challenge 2022 获奖实践）、Mila、独立 NLP 研究者。结构高度同构，可以一起说。

**共同结构**（以 buoyancy99 为典型）：

```
├── main.py                  # 唯一入口：python -m main +name=xx experiment=yy
├── configurations/          # hydra yaml：experiment/algorithm/dataset/cluster 分层组合
├── experiments/             # 实验类：把 algorithm+dataset 接线成可运行任务
├── algorithms/  datasets/   # 可替换部件
└── (CLAIRE/Mila 另加：Docker、pre-commit、SLURM 提交器、复现测试)
```

**核心对象模型**：只有一个对象——**一次可运行的 experiment = config 组合**。一条 `experiment=... algorithm=... dataset=...` 命令本身就是实验的全部定义；W&B 负责记录指标，git 负责记录代码，hydra 负责把"本次运行的确切 config"落盘。**没有任何一个模板试图在 repo 里建模"研究进度"**——Mila 版连文档里都没出现 hypothesis 一词。

**约束机制**：全部在工具层——hydra 的 config schema、pre-commit、conda-lock/Docker 冻结环境、CLAIRE 甚至内置"同一条曲线在不同平台跑出相同数字"的复现测试。AGENTS.md 类约束为零（它们早于 agent 时代，但正因如此成为干净的对照：约束从来不需要靠说教）。

**对我们的启发**：实验侧我们已经对齐（protocol/config/result 三件套约等于它们的 experiment/config/run）。真正的差距在**概念层**：这四种模板从未觉得需要 `claims.md`/`hypotheses.md`——因为 claim 活在论文里，hypothesis 活在实验者脑子里，repo 只需要能重跑实验。我们可以把 hypotheses/claims/decisions 从"agent 必须维护的一等对象"降级为"人写给人看的笔记目录"。

---

### 2.3 Backlog.md —— 人机审查门的样板

**基本信息**：6.8k stars，npm 包 `backlog.md`，定位是"AI 写代码，人审任务"。自己的代码几乎全部由其 dogfooding 产生。

**核心对象**：唯一的一等公民是 **task**，一个 Markdown 文件：

```markdown
---
id: BACK-200
title: Add Claude Code integration with workflow commands during init
status: To Do
assignee: []
created_date: '2025-07-23'
labels: [enhancement, developer-experience]
dependencies: [task-24.1, task-208]
priority: medium
---

## Description
<一段自然语言>

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Claude Code template files are stored in src/templates/claude/
- [ ] #2 backlog init copies .claude directory ...
<!-- AC:END -->
```

**人机边界**（README 原话总结）：
1. **Review the spec** — agent 把想法拆成带 acceptance criteria 的任务，人批准；
2. **Review the plan** — agent 调研代码库，把实施计划写进任务文件，人批准才动手；
3. **Review the code** — 一任务一 PR，diff 保持在人可读规模。

**约束机制**：结构化字段（id/status/dependencies/AC 勾选状态）全部由 CLI 读写——agent 被要求跑 `backlog task create --ac "..."` 而不是手写 frontmatter；status 流转、`task edit`、archive 都有命令；`backlog instructions overview` 给 agent 一份机器生成的操作手册。Markdown 正文部分自由，机器字段零自由。

**对我们的启发**：这是把"复杂概念模型"折叠成"单对象 + 字段化 metadata"的最成功案例。我们的 hypothesis/finding/claim/decision 其实都可以是一种 record 的不同 `type:` 字段，由 `rtmpl` CLI 统一创建/校验，而不是五个各自为政的 Markdown 文件。

---

### 2.4 spec-kit 与 OpenSpec —— Specify→Plan→Tasks→Implement 门控

**基本信息**：spec-kit 138k stars（GitHub 官方），OpenSpec 69.7k stars。两者都是"spec-driven development"：先写可审查的 spec 文档，再让 agent 按计划实施。

**spec-kit 的机制**：模板目录直接给出 `spec-template.md` / `plan-template.md` / `tasks-template.md` / `checklist-template.md`，配一组 slash command（`/speckit.specify` `/speckit.plan` `/speckit.tasks` `/speckit.implement` `/speckit.analyze`）。每个 command 是一个 Markdown 文件，里面写死该阶段的产出格式和"停下来等用户"的位置——**工作流的门就是命令边界**：你不调 `/implement`，它就不写代码。

**OpenSpec 的机制**：更贴近 brownfield。每个变更是一个 `openspec/changes/<name>/` 目录：

```
openspec/changes/add-dark-mode/
├── proposal.md    # 为什么做、改什么
├── specs/         # 需求 + 场景（WHEN/THEN）
├── design.md      # 技术方案
└── tasks.md       # 实施 checklist
```

`/opsx:propose` 生成这四件套，`/opsx:apply` 实施，`/opsx:archive` 归档进 `openspec/changes/archive/`。**变更的生命周期就是目录的移动**：in-flight 在 `changes/`，落地后进 `archive/`，活规范在 `specs/`。没有状态字段，文件系统位置就是状态。

**对我们的启发**：这两个项目验证了我们要的模式已被大规模验证：**人写意图 → agent 扩写成结构化文档 → 人审 → agent 执行**。尤其 OpenSpec 的"目录位置即状态"可以直接借用：`experiments/` 下区分 `draft/` `active/` `done/` 比在 yaml 里维护 status 字段更不容易被 agent 弄错。

---

### 2.5 science-superpowers —— 唯一认真建模科学纪律的，且只用了一个对象

**基本信息**：336 stars，K-Dense 出品，Superpowers（软件方法论技能包）的科学版。16 个 skill，零第三方依赖（POSIX shell + git）。

**核心对象**：只有 **pre-registration**（预注册文档）。工作流是线性技能链：framing → survey → design → **preregister** → setup → execute → investigate anomalies → verify → red-team → report。核心纪律叫 Iron Law："**没有预注册的预测，不得做确证性声明**"。

**约束机制（重点）**：`skills/preregistering-analysis/prereg.sh`，约 100 行 POSIX shell，把抽象纪律变成可审计操作：

```bash
prereg.sh freeze <prereg-file> [raw-data ...]
# 1. 把每个原始数据文件的 git blob 哈希写进文档
# 2. 单独提交该文件："prereg-freeze: <path>" —— 这次 commit 就是时间戳
#    （文件有任何更早的 git 历史就直接 die，禁止重复冻结）
# 3. 把 freeze commit hash 盖回文档 "**Frozen at commit:**" 行，再提交一次

prereg.sh audit [prereg-file ...]
# 纯读操作，输出五项检查，任一 FAIL 则 exit 1：
#   FROZEN     存在 freeze commit
#   STAMP      文档里的 hash 与真实 freeze commit 一致
#   INTEGRITY  文件内容与冻结版本逐字节相同（HEAD 和工作树都查）
#   CHRONOLOGY 没有任何触及 results 路径的 commit 早于 freeze（用 commit 拓扑而非可伪造的时间戳）
#   DATA       冻结时的数据 checksum 仍然匹配
```

配套 SKILL.md 还规定了一条反直觉但关键的规则："**不要在从未运行过的配置上预注册**"——冻结前先跑一遍最便宜的能证伪你的 run，否则预注册只是返工的定金。

**人机边界**：明确区分 confirmatory（需预注册）与 exploratory（允许但永远不得事后改名）；feasibility mode 只能由人类开启和退出，agent 不得自行进出。也就是：**进出模式是人类特权，写在 skill 文本里，但"是否已注册/是否被篡改"是脚本判的**。

**对我们的启发**：这是"代码级强制"的最小可行示范——不需要服务、不需要数据库，一个 shell 脚本 + git 就锁住了最容易被 agent 违反的纪律（事后编假设）。我们模板的 exploration/confirmation 标签分离可以直接抄 `prereg.sh` 的思路：`rtmpl freeze experiments/x/protocol.md` 之后，该文件的任何修改都会让 `rtmpl check` 报 INTEGRITY FAIL。

---

### 2.6 zeropaper —— 全自治的反面教材

**基本信息**：72 stars，全自动论文生成管线（problem discovery → idea → theory → math verification → writing → simulated referee）。架构上极其重：deploy_assets 下有几十个 agent body、fragment 模板、ownership manifest、变体 vocab 替换层。

**它的约束机制**（确实做了代码级强制）：
- `.deploy_manifest.json`：每个 template-owned 路径必须在写站点注册，否则 fail-closed（未登记的路径根本不进部署）；
- canonical/mirror 分离：`CLAUDE.md` 是 canonical，`AGENTS.md` 是生成镜像，手改镜像会被同步脚本覆盖；
- 每个 agent 大改后要派**独立 review agent**（不同模型）审计，"checker 不能是被检查者"写成 repo 级原则；
- 产出 PDF 带不可移除水印标记 autonomous/manual 模式。

**但它自己的 OPERATOR_HANDOVER 暴露了代价**：两条运行中的管线，一条 spec 迭代到 v32、build_failure 6/4 超 cap；另一条 15 次尝试 13 次拿不到 verified receipt、其中 9 次死在项目自建的 replay 校验层。恢复流程是：人类 operator 读 `pipeline_state.json` → 做判断 → 手工把 `status` 改回 `running` 并在 commit message 里写授权范围 → 重新拉起 driver。**自动化越重，收口的人越累**——连作者都在 handover 开头写"Nothing else needs you"，因为判断全部压在那一个人身上。

**对我们的启发**：zeropaper 恰好演示了我们已经踩到的坑——多层 spec 对象 + 循环计数 + receipt 链 + halt 类型，复杂度膨胀到 agent 和人类都读不动。它用代码级强制（manifest、fail-closed、独立 reviewer）也没能救回可理解性。结论不是"加更多强制"，而是"砍掉需要被强制的东西"。

---

### 2.7 eLabFTW / rrtools —— ELN 视角：不可变记录，人写人看

**eLabFTW**（1.4k stars）：最流行的开源电子实验记录本。两个设计与 agent 时代完全同构：
- **Trusted timestamping / blockchain timestamping**：实验记录创建后可锁、可盖时间戳，事后不可改——和 `prereg.sh` 的 freeze 同一思想，说明"不可变 + 可证明时间"是实验记录领域几十年的共识；
- 记录是**人写的叙述**，不是状态机字段。没有"hypothesis 对象"，只有按时间排的实验条目。

**rrtools**（720 stars）：R 社区的可复现研究 compendium。所有产出收进一个 `analysis/` 目录：

```
analysis/
├── paper/{paper.qmd, references.bib}
├── figures/
├── data/{raw_data/, derived_data/}   # 生/熟数据物理分开
└── templates/                       # 期刊模板、引用样式
```

paper.qmd 的页脚自动嵌入 git commit 信息——**产出永远可追溯到代码的具体版本**，零状态文件。

**对我们的启发**：ELN 五十年没变的设计——**追加式、带时间戳、人写人看**——比任何对象模型都长寿。我们 `research-log.md` 按时间追加是对的；`research-state.yaml` 那种"agent 要维护的关系索引"是历史证明活不下去的部分。

---

## 3. 横向对比：对象模型复杂度 vs 约束可执行性

| 项目 | 一等对象数 | 状态文件 | 机器可校验的约束 | 人机门 |
|---|---|---|---|---|
| CCDS | 0 | 无 | `.gitignore`、目录约定 | 无（全人工） |
| ML 模板四家 | 1（experiment run） | 无 | hydra schema、lockfile、复现测试 | 无（全人工） |
| Backlog.md | 1（task） | config.yml（工具配置，非状态） | CLI 管理 frontmatter、AC 勾选 | 3 道（spec/plan/code） |
| OpenSpec/spec-kit | 1（change） | 无（目录即状态） | slash command 模板、checklist | propose→apply 之间人审 |
| science-superpowers | 1（pre-registration） | 无（git 历史即状态） | `prereg.sh` freeze/audit | feasibility 模式人类特权 |
| zeropaper | 10+（spec/receipt/agent/halt…） | pipeline_state.json + manifest | manifest 所有权、独立 reviewer | 人类 operator 手工 halt/resume |
| **我们当前模板** | **6**（hypothesis/finding/claim/decision/experiment/log） | **research-state.yaml + policy.yaml** | `rtmpl check`（一致性）、seed_only 保护 | Inner/Outer loop × manual/semi/full-auto |

规律很直白：**对象数 ≤1 的项目全部活跃且健康；对象数 ≥6 的只有 zeropaper 和我们，而 zeropaper 正在靠一个人类 operator 续命**。

---

## 4. 最佳实践总结

### 4.1 通用设计原则（按证据强度排序）

1. **一个 repo 只建模一个一等对象**。Backlog.md 的 task、OpenSpec 的 change、science-superpowers 的 pre-registration、ML 模板的 experiment run。多于一个对象时，agent 必然混淆边界——我们自己 6 个对象 + zeropaper 10+ 个对象是仅有的反例。

2. **文件系统位置即状态**。OpenSpec 用 `changes/` vs `changes/archive/`、CCDS 用 `raw/` vs `processed/`、zeropaper 用 manifest 登记 vs 不存在。所有"这个对象现在处于什么阶段"的问题都用路径回答，不用字段回答。字段会漂移，路径不会。

3. **机器字段归 CLI，自由文本归 Markdown**。Backlog.md 的 frontmatter、science-superpowers 的 stamp 行，都是"agent 不许手写、只能调命令生成"的区域。任何需要机器校验的信息（id、日期、依赖、哈希）都不该出现在 agent 可自由编辑的正文里。

4. **时间戳和不可变性用 git 实现**。eLabFTW 的 timestamping、prereg.sh 的 freeze commit、rrtools 的页脚 commit hash——没有人发明新的状态数据库。git 的 commit 拓扑天然防伪造（prereg.sh 特意用 ancestry 而非日期）。

5. **人机门是命令边界，不是角色描述**。"人审 plan 再执行"在 spec-kit 里是"你不调 `/implement` 它就停"，在 Backlog.md 里是"task 里的 plan 段人批准才动手"，在 science-superpowers 里是"feasibility mode 只能人类开启"。都是**一个具体的不动作条件**，而不是"agent 应尊重人类权威"这种表述。

6. **探索/确证分离是唯一值得保留的科学概念**。这么多模板里唯一存活的科学方法论约束就是 pre-registration 式的"预测先于结果"。它能活下来因为可以机械化（freeze + audit）；hypothesis 族谱、claim 谱系、决策树活不下来因为没法机械验证。

### 4.2 对我们模板的简化方向

按上面的原则，把当前 6 对象 + 双 loop + automation_mode 收缩成：

```
├── README.md
├── AGENTS.md                  # 只保留：目录语义表 + "跑 rtmpl check" + 禁区目录
├── notes/                     # 人类手写区：想法、假设、文献笔记、决策
│   └── *.md                   # 无 schema，无索引，agent 默认只读
├── experiments/
│   ├── _template/{plan.md,config.yaml,result.md}
│   ├── draft/                 # agent 刚起草、人没批
│   ├── active/                # 人批过 plan（plan.md 已 freeze）
│   └── done/                  # 出了 result.md
├── results/                   # tracker/运行产物，agent 可写
└── .rtmpl/                    # 工具状态（已有）
```

对应动作：

1. **删掉**：`research-state.yaml`（索引维护交给 `rtmpl check` 按需扫描）、`claims.md`/`decisions.md`/`findings.md`/`hypotheses.md`（并入 `notes/`，人类自由写）、`automation_mode` 与 Inner/Outer Loop 配置（不存在就不会被错用）。
2. **保留并机械化**：experiment 目录三件套（plan/config/result）；新增 `rtmpl freeze experiments/<id>/plan.md`——抄 prereg.sh：第一次 commit 即冻结，此后修改会让 `rtmpl check` 报 FAIL；"exploratory → confirmatory 不可逆"由 freeze 历史保证而非文字声明。
3. **人机门改成命令**：`rtmpl submit <experiment>`（agent 把 draft/ 移到待审）→ 人看 `plan.md` → `rtmpl approve`（freeze + 移 active/）→ agent 只在 active/ 实验上跑。agent 侧的全部规则收敛成一句："没有 `active/` 下的 plan，不动手执行"。
4. **dashboard 等派生物**：若要保留，放 `derived/` 目录并整体标"agent 生成、随时可删"，与 notes/ 物理隔离。

### 4.3 迁移成本估计

- `rtmpl freeze/approve/submit` 三个子命令：prereg.sh 才 100 行 shell，我们的 Python 版本约半天到一天。
- `rtmpl check` 扩展 INTEGRITY/CHRONOLOGY 检查：复用 git log，再加半天。
- 模板文件删减 + AGENTS.md 重写：1-2 小时。
- 已有的 `seed_only`/`--force` 保护机制不变，反而更简单——notes/ 整个目录标 seed_only 即可。

---

## 5. 参考链接

- CCDS opinions（raw data 不可变）：https://cookiecutter-data-science.drivendata.org/opinions/
- Backlog.md 三道审查门：https://github.com/MrLesk/Backlog.md#why-backlogmd-in-the-ai-era
- science-superpowers prereg.sh：https://github.com/K-Dense-AI/science-superpowers/blob/main/skills/preregistering-analysis/prereg.sh
- spec-kit 模板与命令：https://github.com/github/spec-kit/tree/main/templates
- OpenSpec changes/specs 模型：https://github.com/Fission-AI/OpenSpec
- zeropaper OPERATOR_HANDOVER（全自治收口实况）：https://github.com/alejandroll10/zeropaper/blob/main/OPERATOR_HANDOVER.md
- feynman autoresearch prompt（有界实验循环）：https://github.com/Companion-Inc/feynman/blob/main/prompts/autoresearch.md

# HANDOFF — skills-driven-ara-template 框架化改造

> 本文档由前置 opencode 会话整理，供后续能力更强的 agent 接手。
> **内容范围**：用户的原始目标、用户已确定的设计决策与方向、客观探测事实。
> **不含**前置 agent 自己的设计主张或方案选型（用户明确要求）。
> 文档完成后已将仓库工作树回退到改动前基线（最近提交 `a967610`）。

---

## 0. 一句话目标

把当前这个「Markdown 建议型科研模板仓库」改造成一个**用代码逻辑强制约束 code agent 行为的研究框架（命名 `rk`）**，支持 human+agent 协同进行 ML 研究，最小化用户配置项，使 code agent 能直接基于它启动新的科研项目。

---

## 1. 背景与动机（用户原意）

1. **当前模板缺乏强制力**：用 Markdown 告诉 agent「应使用 `remote_run.sh` / `remote_env.sh`」，但 agent 可以绕过、直接运行 `python`，导致环境变量未加载 → 静默错误。用户要求用「工程/代码逻辑」严格约束 agent，而非靠文档建议。
2. **现有脚本存在重复声明**：`remote_env.sh` 的环境变量在多个 `remote_*.sh` 脚本里被重复声明，会造成漂移。需要单一来源。
3. **两类读者必须分离**：模板既要服务于「用框架做研究」的 agent，也要服务于「开发框架本身」的 agent；这两者的指引不能混在一起。
4. **远程执行的可靠性**：长任务必须能在本地会话断开后继续，并能被观测（参考 `remote-terminal-tool-strategy` 技能：远程 tmux、稳定日志、心跳、完成标记）。

---

## 2. 用户已确定的设计决策

### 2.1 框架命名
- 框架运行时命令定名 **`rk`**（取自 ResearchKit，简短易记）。

### 2.2 两层仓库结构（用户给出的目标形态）
```
skills-driven-ara-template/
  AGENTS.md                  # 给「开发这个模板/框架」的 agent 看（元层）
  docs/                      # 框架设计、开发记录、决策
  templates/
    ara-research-workspace/  # 真正会被复制出去的模板
      AGENTS.md              # 给「复制后项目里」的 agent 看（项目层）
      README.md
      scripts/
      remote/
      research/
      experiments/
      ...
```
- **根 `AGENTS.md`** = 框架开发元层（给开发/迭代框架的 agent）。
- **`templates/ara-research-workspace/AGENTS.md`** = 项目层（给基于模板做研究的 agent）。
- `docs/` 用 **ADR（决策记录）** 形式沉淀每个决策；每次对框架的优化都用 **git commit** 记录。

### 2.3 双执行模式（都要支持）
- **`remote-sync`**（主用）：code agent 跑在本地 Mac，用 **Mutagen** 把代码同步到远程服务器执行。Mac 侧保留完整 MCP（Zotero / alphaxiv / Semantic Scholar 等）。
  - **Mutagen 同步方向设为 one-way 覆盖**：一切以 Mac 本地为唯一真相源，服务器端为镜像、被动跟随。
- **`server-local`**：代码库直接放在 GPU 服务器上运行。
- **两种模式之间不设计互转**：用户实际使用中很少在一个项目里做 remote-sync ↔ server-local 的转换；一个项目若是 remote-sync 就一直是 remote-sync。框架**不需要支持两种模式之间的迁移/转换**。
- **跨服务器或跨模式切换**：仅当实现不复杂时才纳入设计（nice-to-have），否则不强求。

### 2.4 框架运行时源码的位置
- 框架运行时源码**放在模板内部**，使 code agent 在实际项目里可以**直接编辑框架源码**来适配当前服务器/修复 bug；通用的改进再**合并回上游模板**。
- 用户希望这条「用实际使用来不断优化模板」的回路尽量**优雅**（具体机制见 §4 开放问题）。

### 2.5 适配范围
- **当前只适配 batchcom**；把基础框架打好，使其后期容易扩展不同访问方式。
- **4090-ts 等其他服务器使用频率低，暂不适配**，按需再做。

### 2.6 账号与隔离模型（针对新 batchcom）
- batchcom 现为**单人独占一个 Docker 镜像**（Docker-in-Docker 当前关闭，无需 Docker 隔离）。
- **暂不按多人共享设计**；将来出现多人共用场景再单独设计。

### 2.7 支持的 code agent
- 优先支持 **OpenCode** 与 **CodeX**。
- OpenCode 已能自动加载 `.opencode/` 下的 agent（如 `remote-exec`）。
- **CodeX 存在等价的 subagent 机制**；具体用法由接手 agent 自行检索确认并补齐适配。

### 2.8 配置自动化与统一变量（最小化用户配置）
- 框架要把 **SSH、SSH MCP、Mutagen 等**配置工具纳入考虑（参考 `remote-terminal-tool-strategy` 技能）。
- 目标：自动生成所需配置（如 ssh 别名、SSH MCP `servers.toml`、Mutagen 配置），**让用户需要手填的配置项越少越好**，让 agent 拿到就能直接开新科研项目。
- **服务器别名统一**：所有生成的配置项（ssh config、SSH MCP、Mutagen 等）都引用**同一个服务器别名**，该别名在**初始化时由环境变量统一设定**，避免多处命名不一致。
- **环境变量驱动**：沿用现有框架已有的环境变量风格，用环境变量统一表达 dataset 路径、model 路径、code 路径等；初始化时一次性注入，运行时各脚本只读取、不重复声明（直接解决 §1.2 的重复声明/漂移问题）。

### 2.9 数据集/模型路径
- 不同服务器上数据集与模型路径不同（例如某服务器在根目录 `data/`，batchcom 在 `dataset-local/` 下），应在**复制框架后或初始化时通过环境变量**等方式处理。

### 2.10 bootstrap（远程基础环境初始化）
- batchcom 基础镜像很瘦（见 §3.1），缺失多种工具，需一次性 bootstrap。
- 用户要求前置 agent 直接完成该 bootstrap。
- **bootstrap 不属于 `rk` 运行时** —— 框架默认消费一个「已完备的操作系统」。（bootstrap 是放进 `rk` 作为子命令、还是作为独立提示词/脚本交给 agent 手动执行，用户未拍板，见 §4。）

### 2.11 本次回退
- 撤销另一个 agent 对本仓库的**最新未提交改动**；已提交版本（`a967610` 及之前）保留。（已执行，见 §5。）

---

## 3. 客观探测结果

### 3.1 目标服务器：batchcom（新机，当前目标）

**访问**
- `ssh -p 30174 batchcom@203.176.93.143`，密钥 `~/.ssh/id_rsa`。
- 旧机 `ssh -p 30232 batchcom@61.172.170.106` **已废弃**（见 §3.3）。
- 本地 `~/.ssh/known_hosts` 存在 `[203.176.93.143]:30174` 的残留旧 host key，首次连接会报 host key changed，需更新。

**身份与权限**
- 用户 `batchcom`，uid=1000，单用户；**passwordless sudo = YES**。

**算力**
- 8 × NVIDIA A100-SXM4-80GB（探测时全空闲）；96 CPU 核 / 960 GB 内存；CUDA 13.0。

**软件现状**
- 已有：Python 3.12.12、conda 24.11.3（`/opt/conda`）、pip、nvcc。
- **缺失**：`git`、`tmux`、`uv`、`mutagen`、`mamba`、`node`、`npm`、`opencode`、`codex` 均未安装。
- Docker 未安装（Docker-in-Docker 关闭）。

**存储三层（决定框架的路径策略）**

| 挂载 | 大小 | 类型 / 速度 | 持久化 | 备注 |
|---|---|---|---|---|
| `/`（overlay，HOME `/home/batchcom` 在此） | 50G | overlay / 极快 | **❌ 实例停止即丢**（除非保存镜像） | `/opt/conda` 在此 → 默认 conda env 会随重启丢失 |
| `/home/dataset-local` | 5.4T | xfs 本地 NVMe / 极快 | **✅ 用户已设持久化** | 可写；适合 conda env、数据集、cache、训练 IO |
| `/home/dataset-assist-0/research` | 9.8T | NFS / 快 | **✅ 跨重启持久** | 可写；内有平台身份文件 `masonking1319@team.edu.sixoner.com.json` |
| `/tmp` | 873G | 独立盘 | — | — |

**网络**
- 裸测：`huggingface.co` 与 `hf-mirror.com` **不通**；`pypi` / `tuna-pypi` / `github` / `modelscope` **可达**。
- **用户的网络方案**：本地用 **chezmoi** 管理 config，可应用到 server 端并启用 **chezmoi server 模式** → 远程提供 **7890 端口代理** → HuggingFace、HF-Mirror、GitHub 等均可正常访问。因此 HF 实际可用，模型可走 HF / HF-Mirror（modelscope 作为备选）。

**SSH / 配置**
- 远端 `~/.ssh` 仅含平台注入的 host keys 与 `authorized_keys`，**无用户私钥**；无 git 全局配置。

### 3.2 本地 Mac 环境
- 模板仓库：`/Users/macbookair/code/skills-driven-ara-template`（git 仓库，最近提交 `a967610`）。
- 用 **chezmoi** 管理 dotfiles（可推送到 server + 启用 server 模式作代理，见 §3.1 网络方案）。
- 已安装 **Mutagen**（用于 remote-sync 模式）。
- OpenCode 配置见 `.opencode/opencode.jsonc`，带 MCP server：Zotero、alphaxiv、Semantic Scholar、SSH MCP、context7 等。
- `~/.ssh/config` 已有多台服务器别名（如 `4090-ts` = `geyulong@4090-710:22`、多台 918/jyr/3090/4090 等）；**尚无 batchcom 别名**。
- 当前根 `AGENTS.md`（`a967610` 版本）描述的是 skills-driven ARA research workspace，含 `scripts/remote_*.sh`、Mutagen、profiles 的远程执行框架与验证命令。

### 3.3 已废弃机器（旧 batchcom，仅备查）
- `ssh -p 30232 batchcom@61.172.170.106` —— **已废弃**，换为 §3.1 新机。
- 旧机曾探测到的「3 人共享账号 / `/data/set/local` / docker 需 sudo」等结论**不再适用**；当前按 §2.6 单人独占模型设计。

---

## 4. 用户提出的开放 / 待决问题（交由接手 agent 推进或与用户确认）

1. **bootstrap 的归属**：作为 `rk` 的子命令（`rk bootstrap`），还是作为独立提示词/脚本，让 agent 拿到新系统时手动执行？用户倾向 bootstrap 不进 `rk` 运行时，但未最终拍板。
2. **「用实际使用优化模板」回路如何更优雅**：框架源码随项目流转、通用改进合并回上游模板的具体机制（git subtree / 独立 remote / 其他）尚未选定。

> 已澄清（不再列为开放问题）：
> - **模式切换**：两种模式之间不互转（见 §2.3）；跨服务器/跨模式切换仅在实现不复杂时才做。
> - **CodeX subagent**：等价机制存在，由接手 agent 自行检索确认（见 §2.7）。

---

## 5. 当前仓库状态（本会话结束态）

- 已对 9 个被改文件执行 `git restore`（回到 `a967610`）。
- 已删除未跟踪项：`remote/`、`scripts/remote_doctor.sh`、`scripts/remote_selftest.sh`。
- 工作树 = `a967610` 基线 + 本 `HANDOFF.md`（未提交）。
- `git status`：clean（除本文件）。

## 6. 相关技能与既有约定（接手 agent 可参考）
- `remote-terminal-tool-strategy`：远程会话/传输工具选型（SSH / SSH MCP / PTY / tmux / SCP）；长任务须用**远程 tmux** + 稳定日志 + 心跳 + 完成标记。
- `using-superpowers`：流程类技能优先（brainstorming → writing-plans → executing-plans → verification-before-completion）。
- 仓库 `AGENTS.md`（`a967610` 版）中已有的目录约定（`research/`、`literature/`、`experiments/`、`src/`、`external/`、`ara/` epilogue 等）与远程执行脚本约定，可作为改造基线参考。

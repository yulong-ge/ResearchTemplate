# 技能路由指南：当前研究工作空间

`autoresearch` 技能用于编排研究工作。领域特定的技能处理专门的任务。请参考此文档，在当前工作空间中实际已安装的技能中进行选择和切换。

## 路由原则

当任务具有特定的领域属性时，请识别并找到最贴近且已安装的对应技能，在执行操作前务必先阅读其 `SKILL.md`。优先选择能直接匹配当前瓶颈的最特异化技能。

## 已安装技能映射表

### 研究规划与方向指导

| 任务 | 技能 |
|---|---|
| 评估某研究方向是否值得推进 | `idea-evaluator` |
| 生成或提炼研究构想（Research Ideas） | `brainstorming-research-ideas` |
| 系统性地探索更具新颖性的研究方向 | `creative-thinking-for-research` |
| 编排完整的研究闭环 | `autoresearch` |

### 研究记忆与追溯（Provenance）

| 任务 | 技能 |
|---|---|
| 编译结构化的研究智能体原生制品（ARA） | `ara-compiler` |
| 在完成一个有意义的工作单元后记录溯源信息 | `ara-research-manager` |
| 审计某项学术主张在认识论上是否具有足够论据支撑 | `ara-rigor-reviewer` |

### 机制可解释性（Mechanistic Interpretability）

| 任务 | 技能 |
|---|---|
| 分析 Transformer 电路与内部机制 | `transformer-lens-interpretability` |
| 训练稀疏自编码器（SAE）以用于特征发现 | `sparse-autoencoder-training` |
| 运行基于干预的因果分析 | `pyvene-interventions` |
| 运行远程激活打补丁（Activation Patching）与干预工作流 | `nnsight-remote-interpretability` |

### 图像生成与扩散模型

| 任务 | 技能 |
|---|---|
| 开展 Stable Diffusion 生成或适配工作流相关工作 | `stable-diffusion-image-generation` |

### 训练、微调适配与扩展

| 任务 | 技能 |
|---|---|
| 参数高效微调（PEFT）工作流 | `peft-fine-tuning` |
| 采用轻量级抽象的多 GPU 或分布式训练 | `huggingface-accelerate` |

### 评估与实验追踪

| 任务 | 技能 |
|---|---|
| 标准模型评估及基准评估框架（Benchmark Harness）使用 | `evaluating-llms-harness` |
| 在 W&B 中追踪实验、指标、制品与仪表盘 | `weights-and-biases` |
| 在本地检查训练曲线与标量日志 | `tensorboard` |
| 使用 SwanLab 追踪实验 | `experiment-tracking-swanlab` |

### 研究写作与学术图表

| 任务 | 技能 |
|---|---|
| 撰写或修改机器学习/人工智能（ML/AI）论文章节 | `ml-paper-writing` |
| 设计或审视学术论文技术图表（Figures） | `figure-designer` |
| 生成出版物质量的学术图表（Plots） | `academic-plotting` |

## 常见研究工作流

### “我正在开启一个新的研究方向”

1. 阅读 `research/overview.md` 和 `research/findings.md`
2. 使用 `brainstorming-research-ideas` 或 `creative-thinking-for-research` 生成或提炼候选方案
3. 如果其中某候选方案需要进行结构化的可行性评判（Go/No-go 判断），请启动一个新的子智能体（Subagent），并在其中使用 `idea-evaluator`。这样可以保持评估环境与当前活跃工作上下文相互隔离
4. 将选定的方向记录在 `research/overview.md` 中，将候选/搁置/拒绝方向记录在 `research/ideas.md` 中

### “我需要运行一个可解释性实验”

1. 在 `transformer-lens-interpretability`、`sparse-autoencoder-training`、`pyvene-interventions` 和 `nnsight-remote-interpretability` 中做出选择
2. 如果该实验旨在证实或证伪某项学术主张，请在 `experiments/protocols/` 下撰写一份确证性协议（Confirmatory Protocol）
3. 将实验输出保存在 `experiments/results/<experiment-id>/` 目录下
4. 更新 `experiments/logs/`、`research/findings.md` 和 `research/research-log.md`

### “我需要训练或适配一个模型”

1. 涉及扩散模型工作流时，使用 `stable-diffusion-image-generation`
2. 适配器或低阶自适应（Low-Rank Adaptation）时，使用 `peft-fine-tuning`
3. 本地多 GPU 可扩展执行时，使用 `huggingface-accelerate`
4. 配合使用 `weights-and-biases`、`tensorboard` 或 `experiment-tracking-swanlab` 追踪运行指标

### “我需要评估实验结果是否足够扎实，以决定是否保留”

1. 将当前对实验结果的阐释与分析更新到 `research/findings.md`
2. 若该学术主张至关重要，请使用 `ara-rigor-reviewer` 评估其论证严密性
3. 在完成有意义的综合与提炼步骤后，使用 `ara-research-manager` 归档

## 发现与添加技能

当前工作空间中仅预装了上述专注的研究技能子集。

若未来项目需要当前未安装的能力，请浏览 AI Research Skills 仓库，并通过 `npx skills` 命令添加缺失的技能，切勿自行拼凑临时的本地替代方案：

- `https://github.com/Orchestra-Research/AI-research-SKILLs`

建议仅安装能够真正解决当前项目瓶颈的技能，以保持工作空间聚焦，便于智能体高效路由。

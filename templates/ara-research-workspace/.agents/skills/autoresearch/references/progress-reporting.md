# 进度报告规范：研究成果演示 (Progress Reporting)

当研究工作取得了值得分享的阶段性成果时，请制作一份精美的演示报告 —— 这不应是冰冷的数据堆砌，而是一个辅以精美图表的研究故事。

## 何时进行报告

你可以自主决定研究进展是否已达到需要进行成果演示的阶段。在以下情况下考虑生成进度报告：

- 在外循环反思中识别出显著的共性规律后。
- 当优化轨迹显示出清晰且持续的性能提升时；如果当前研究不是优化型任务，可以改用关键诊断对比图或机制图。
- 在发生方向性调整 (Pivot) 之后 —— 向用户阐明为什么调整方向。
- 在重大科学决策上需要人类研究员共同讨论与做出决定前。
- 当研究得出结论准备收尾、开始撰写学术论文前。

只有当用户明确要求提供进度演示报告，或工作交接文档需要时，才生成报告。

## 什么是优秀的研究演示报告

一份出色的研究进度报告应当读起来像是一场生动的学术报告，而不是数据库的原始查询结果。它应当：

1. **讲好一个故事**：我们为什么开始（研究背景）、我们尝试了什么（探索过程）、我们发现了什么（实验结果）、以及这意味着什么（认知洞察）。
2. **用数据说话，辅以直观呈现**：包含曲线图、对比表格 —— 决不能只有枯燥的文字。
3. **保持重点突出**：高亮展示最具启发性的科学发现，拒绝流水账般罗列每一次微小的实验。
4. **以明确的规划收尾**：说明下一步将做什么以及为什么这么做。

## 推荐的章节结构

根据当前研究的具体情况灵活调整这些章节。跳过不相关的章节，根据需要增加特定的自定义章节。

### 1. 研究问题与动机 (Research Question & Motivation)
- 我们正在探究什么课题？为什么这项研究重要？
- 简短的一到两个段落，确保不熟悉该项目的人也能迅速读懂。

### 2. 研究方法 (Approach)
- 我们的技术方案是什么？正在优化什么指标？
- 用一句话高度概括双循环架构。

### 3. 核心证据图 (Core Evidence Figure)
- 优化型任务可使用 Karpathy-style 进展曲线：X 轴为实验序号或累计耗时，Y 轴为代理指标。
- 诊断型或机制型任务可使用关键对比图、轨迹图、频谱图、消融表或架构图。
- 只展示能支撑当前科学叙事的 1-2 张核心图，不要为了套模板强行绘制优化轨迹。

### 4. 关键发现 (Key Findings)
- 展示 2-3 个最重大的实验结果，并附带强有力的科学实证。
- 包含图表、指标表格以及对比图。
- 深刻阐述这些结果为什么重要，而不仅仅是罗列数据。

### 5. 实验探索历程 (Decision Map)
- 精简版的一级与二级假设树状图。
- 专注于科研心路历程：为什么选择这些方向，它们分别让我们学到了什么。
- 既要包含成功的经验，也要包含富有启发性的失败教训。

### 6. 当前认知 (Current Understanding)
- 提取自 findings.md 的学术叙事，以更直观、引人入胜的方式呈现。
- 针对所观察到的规律，我们目前能给出的最佳物理解释是什么？

### 7. 下一步计划 (Next Steps)
- 计划开展哪些实验，为什么？
- 还有哪些核心问题悬而未决？
- 是否有任何关键决策需要人类研究员进行输入？

## 可选：优化轨迹曲线图的绘制

当研究任务有明确代理指标时，可以使用一张展示代理指标随实验轮次演进的图表。若当前任务是机制诊断、模型比较或数据分析，请改用更贴合证据的图表。

以下是轻量级的实现（基于 SVG 格式，无需安装任何第三方绘图库依赖）：

```python
def generate_trajectory_svg(trajectory_data, width=800, height=400):
    """生成 SVG 格式的优化轨迹图表。

    trajectory_data: 包含数据点的列表，每个数据点格式为 {"run": int, "metric": float, "label": str}
    """
    if not trajectory_data:
        return "<p>暂无实验数据。</p>"

    metrics = [d["metric"] for d in trajectory_data]
    min_m, max_m = min(metrics), max(metrics)
    margin = (max_m - min_m) * 0.1 or 0.1
    y_min, y_max = min_m - margin, max_m + margin

    padding = 60
    plot_w = width - 2 * padding
    plot_h = height - 2 * padding
    n = len(trajectory_data)

    def x_pos(i):
        return padding + (i / max(n - 1, 1)) * plot_w

    def y_pos(v):
        return padding + plot_h - ((v - y_min) / (y_max - y_min)) * plot_h

    # 构建 SVG
    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += f'<rect width="{width}" height="{height}" fill="#1a1a2e" rx="8"/>'

    # 网格背景线与 Y 轴刻度
    for i in range(5):
        y = padding + i * plot_h / 4
        val = y_max - i * (y_max - y_min) / 4
        svg += f'<line x1="{padding}" y1="{y}" x2="{width-padding}" y2="{y}" stroke="#333" stroke-dasharray="4"/>'
        svg += f'<text x="{padding-8}" y="{y+4}" fill="#888" text-anchor="end" font-size="11">{val:.3f}</text>'

    # 绘制基线 (Baseline) 横线
    baseline = trajectory_data[0]["metric"]
    by = y_pos(baseline)
    svg += f'<line x1="{padding}" y1="{by}" x2="{width-padding}" y2="{by}" stroke="#ff6b6b" stroke-dasharray="6" opacity="0.7"/>'
    svg += f'<text x="{width-padding+5}" y="{by+4}" fill="#ff6b6b" font-size="10">基线基准 (baseline)</text>'

    # 数据连接折线
    points = " ".join(f"{x_pos(i)},{y_pos(d['metric'])}" for i, d in enumerate(trajectory_data))
    svg += f'<polyline points="{points}" fill="none" stroke="#4ecdc4" stroke-width="2"/>'

    # 数据点圆形
    for i, d in enumerate(trajectory_data):
        cx, cy = x_pos(i), y_pos(d["metric"])
        svg += f'<circle cx="{cx}" cy="{cy}" r="4" fill="#4ecdc4"/>'

    # 标题与 X 轴标签
    svg += f'<text x="{width/2}" y="24" fill="#eee" text-anchor="middle" font-size="14" font-weight="bold">优化轨迹 (Optimization Trajectory)</text>'
    svg += f'<text x="{width/2}" y="{height-10}" fill="#888" text-anchor="middle" font-size="11">实验轮次 (Experiment Run)</text>'
    svg += '</svg>'
    return svg
```

你可以直接将生成的 SVG 代码内联嵌入到 HTML 进度展示文件中。同时，在发生明显性能跃升的数据点上标注出简短的中文字符说明。

## HTML 成果演示模板

使用 [templates/progress-presentation.html](../templates/progress-presentation.html) 作为起始点。它为你预置了：
- 极其优雅的、符合研究审美的高级暗黑主题 CSS 样式。
- 自适应响应式布局。
- 与推荐结构高度吻合的章节框架。
- 用于嵌入核心证据图的 SVG/图片占位符。

使用你真实的研究数据替换占位符文本。根据你当前研究的实际需求，灵活地添加、删除或重新编排各章节。模板是骨架，而不是束缚。

### 持续运行时 (Claude Code) 场景下的展现

仅在用户明确要求提供进度演示报告时生成 HTML，并在生成后，告知用户通过以下命令在本地浏览器打开查阅：

```bash
open paper/progress-001.html
```

如果需要，可以将其转换为 PDF。常用的工具选项包括：
- 使用 Python 的 `weasyprint` 库将 HTML 直接转为 PDF。
- 使用 `matplotlib` 将图表直接输出为 PDF 格式。
- 构建极简的 markdown → PDF 工具链。

将输出的 PDF 路径记录在当前工作日志中，或在用户索要报告时直接在聊天中提供。

## 提高演示质量的科学小贴士

- **每一章节专注于一个核心科学洞察** —— 拒绝信息过载。
- **所有图表必须清晰标注轴线名称和单位**。
- **色彩搭配保持一致** —— 例如，统一使用绿色系代表性能提升，红色系代表原始基准。
- **在数据有波动时，尽可能包含置信区间**或误差线。
- **将最能支撑当前科学叙事的核心证据图放在前排位置** —— 它是让读者瞬间理解贡献的锚点。
- **务必以清晰明确的下一步计划收尾** —— 人类应当不需要提问就能完全了解下一步的科学规划。

# ResearchTemplate

用 `rtmpl new` 给科研项目建立统一的目录。从本仓运行时，在命令前加 `uv run`。单主题项目在仓库根目录运行一次，多主题仓库对每个研究主题各运行一次。

```sh
rtmpl new my-project
rtmpl new --path /path/to/existing-project
rtmpl new
```

省略路径时使用当前目录，`init` 是 `new` 的别名。已有目录和文件原样保留，新目录用 `.gitkeep` 随 Git 检出。

```text
<研究主题>/
├── literature/    # 阅读的论文和笔记
├── references/    # 数据集说明、评测协议和外部资料
├── paper/         # 自己的论文、报告和写作草稿
├── src/           # 自有代码
└── experiments/   # 实验配置、专用分析脚本、汇总结果和代表图
```

默认初始化只补目录。终端会输出带目标绝对路径的 Agent Maintenance 提示词。需要文档和工具链时，把这段提示词交给 Agent。

## 已受管的 BatchCom 项目

旧项目继续使用 `rtmpl status`、`rtmpl update` 和 `rtmpl repair`。如需基于完整旧模板创建受管项目，显式运行 `rtmpl new my-project --template batchcom-research --var conda_env=ml --no-input`。用 `rtmpl list` 查看受管模板，`rtmpl adopt` 可为从旧模板手工复制的项目建立基线。

开发与验证见 [AGENTS.md](AGENTS.md)，旧项目同步规则见 [更新保护](docs/subsystems/update-protection.md)。

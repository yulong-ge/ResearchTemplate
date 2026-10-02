# BatchCom 研究工作区

## 工作方式

- 人为每个实验或工程任务写一个 Plan（`docs/plans/`）。Plan 给出问题、背景、可读文件、可改路径、
  命令、资源和停止条件。
- 执行前，Agent 先给出具体方案：要改的文件、要跑的命令、预期产物和风险，然后等人明确同意。
- Agent 只读 Plan 指定的上下文，只改 Plan 允许的路径。需要更多上下文或更大范围时，停下来说明原因，
  等人更新 Plan。
- Agent 汇报原始输出、报错和观察，不替人下结论。结果解释、笔记整理、下一步计划由人决定。

## 目录归属

| 路径 | 归属 | Agent 默认行为 |
|---|---|---|
| `docs/plans/` | 人 | 只读；人明确要求时才起草或修改 |
| `notes/`、`literature/`、`paper/` | 人 | 只读；Plan 明确点名的文件除外 |
| `experiments/<名字>/` | 人定目录名 | 写入 Plan 要求的日志、指标和产物 |
| 项目代码与配置 | 项目维护者 | 只改 Plan 列出的路径 |
| `.rtmpl/` | `rtmpl` | 不编辑，不当作研究上下文 |

## 路径与存储

`src/paths.py` 是唯一的路径来源，项目值由 `.rtmpl/config.yaml` 渲染；脚本里不要硬编码服务器路径。

- 研究 NFS：`SHARED_DATA_ROOT`、`SHARED_MODEL_ROOT`、`DATA_ROOT`、`MODEL_ROOT`、`RESULTS_ROOT` 是正本位置。
- 本地 NVMe：`DATA_CACHE`、`LIB_CACHE` 只做加速缓存，正本留在研究目录。
- 系统盘、`/home/batchcom`、`/tmp` 不存放数据、模型、结果、缓存或环境。

## 环境与执行

- Mac 用 `uv` 管理环境，只做 CPU 检查，不跑 GPU 任务。
- BatchCom 用 conda 提供 CUDA/torch，用 `uv` 管理项目环境；conda 环境在 `/home/dataset-local/conda/envs`。
- 在 BatchCom 上用 tmux 运行：`conda activate <env> && uv run python ...`。
- 从 Mac 用原生 SSH + tmux 操作。GPU 任务开始前先检查 `nvidia-smi`、磁盘空间和 torch CUDA 可用性。

## Git 与验证

原始产物不进 Git。改动后运行项目测试和相关命令检查。`rtmpl status` 只报告模板文件差异，不代表研究进度。

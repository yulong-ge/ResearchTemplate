# 实验产物

每次运行或每批实验一个目录，名字自己定，例如 `experiments/baseline-check/` 或
`experiments/2026-09-22-ablation/`。

这里放 Plan 要求的日志、指标、配置、图表等原始产物，目录内部没有固定结构。
实验的动机、做法和结论写在对应的 Plan 里，不在这里另写说明文件。
Agent 只在 Plan 指定了目录和产物时写入这里。

大文件和正本资产放在 `src/paths.py` 定义的位置；Git 里只保留有用的引用和少量复现元数据。

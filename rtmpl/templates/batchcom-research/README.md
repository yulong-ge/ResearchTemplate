# BatchCom 研究项目

人主导、Agent 辅助的深度学习研究工作区。人写笔记和 Plan，Agent 按 Plan 执行代码修改和实验，
并汇报原始结果。`rtmpl` 只管理模板文件本身，不记录研究进度。

## 目录

| 位置 | 用途 |
|---|---|
| `docs/plans/` | 每个实验或工程任务一个 Plan：计划、执行范围、结果和结论都写在同一个文件里 |
| `notes/daily/` | 日报 |
| `notes/weekly/` | 周报 |
| `notes/templates/` | Plan、日报、周报、复盘的模板 |
| `notes/environment.md` | 环境、数据和模型登记 |
| `experiments/<名字>/` | 日志、指标、配置、图表等原始产物 |
| `literature/notes/` | 论文笔记 |
| `paper/` | 论文稿件 |
| `external/` | 第三方代码（直接拷贝，不用 submodule） |
| `.rtmpl/` | 模板元数据，不要手动编辑 |

## 一个任务的流程

1. 复制 `notes/templates/plan.md` 到 `docs/plans/YYYY-MM-DD-<简述>.md`，写清问题、背景和 Agent 可改的范围。
2. 让 Agent 读这个 Plan，给出执行方案；你确认后再让它执行。
3. Agent 把产物写到 Plan 指定的 `experiments/<名字>/`，在对话里汇报结果。
4. 你在 Plan 末尾写结果和结论；需要的话在日报/周报里链接这个 Plan。

## 日报、周报、复盘

- 日报：`notes/daily/YYYY-MM-DD.md`，用 `notes/templates/daily.md`。
- 周报：`notes/weekly/YYYY-Www.md`，用 `notes/templates/weekly.md`。
- 复盘：一个实验或阶段结束时，在对应 Plan 末尾或单独文件里按 `notes/templates/review.md` 写。

模板是普通 Markdown，可以直接在 Obsidian 里用（把核心插件「模板」的目录设为 `notes/templates`，
`{{date}}` 会自动替换），也可以复制到 Notion 或飞书。

## 存储

存储路径统一从 `src/paths.py` 导入。共享资源用 `SHARED_DATA_ROOT`、`SHARED_MODEL_ROOT`；
项目资源用 `DATA_ROOT`、`MODEL_ROOT`、`RESULTS_ROOT`。`DATA_CACHE`、`LIB_CACHE` 是可丢弃的缓存。

Zotero MCP 通过 `ZOTERO_LOCAL=true` 连接本机 Zotero 桌面端，不需要 Web API key。

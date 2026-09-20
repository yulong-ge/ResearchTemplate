# E<id>：<实验名称>

复制到 `experiments/<id>/protocol.md` 后填写。未知信息保留 `unknown`，没有授权不得启动。

## 身份与版本

```yaml
id: E<id>
revision: 1
mode: exploratory  # exploratory | confirmatory
status: candidate  # candidate | active | waiting | closed
execution_status: draft  # draft | approved | running | completed | superseded
authorization_status: pending  # pending | approved | expired | revoked
loop_mode: inherit_policy  # auto | human | inherit_policy
hypothesis_refs: []
authorized_by: null
created_by: unknown
recorded_at: null
```

## 问题、预测与方法

- 要检验的 H 及版本：
- 事前预测和削弱条件：
- 改变变量、对照和固定条件：
- 数据版本、模型、初始化和预算口径：

## 评估契约

- 主要/次要指标及实现版本：
- 数据、样本量、采样和评估随机性：
- checkpoint 选择规则：
- 重复设计、统计聚合和不确定性：

## 实际配置与锁定

引用 `config.yaml` 和覆盖项。记录协议内容哈希或提交，执行时由 tracker 捕获准确版本。

## 有效性与停止条件

记录 baseline、数据加载、收敛/数值检查、排除规则、有限重试、预算停止条件和需要回到人工决定的情况。

## 修订记录

| 时间 | 版本 | 变更 | 已看到结果 | 对证据和授权的影响 |
|---|---|---|---|---|

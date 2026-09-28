# 设计中央仓结构

## 本节目标

用信息生命周期决定 AGENTS、docs、specs、services 和 scripts 的边界。

## 前置输入

准备通过验证的 YAML 和一张资产分类表。

## 为什么要做

目录不是装饰；它决定 Agent 从哪里读取事实、在哪里写需求材料、在哪里改代码。

## 操作步骤

先创建空目录树；把稳定事实放 docs，把需求材料放 specs，把挂载留给 services，把确定性动作放 scripts。

## 关键文件解析

`examples/expected-tree.txt` 是最小结构合同；生成仓的 build-record 解释结构来源。

## 设计取舍

不预建空 Skills 和 Tools；没有真实能力时，占位目录会制造错误信号。

## 验证命令与预期结果

运行 `python3 -m central_repo_scaffold plan --config examples/domain.yaml --output /tmp/manual-central`，确认不写文件。

## 常见错误及根因

把所有说明塞进 README 会让入口膨胀；根因是缺少渐进式加载层级。

## 学员练习

手工创建目录并与 expected-tree 对照，不复制模板正文。

## 完成标准

每个目录有唯一职责，关键规则两到三跳可达。

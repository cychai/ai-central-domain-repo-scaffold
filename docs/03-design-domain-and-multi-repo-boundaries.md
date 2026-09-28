# 设计领域与多仓边界

## 本节目标

形成多服务 YAML，明确读写边界和挂载策略。

## 前置输入

完成服务仓分析表，并选定中央领域名称与仓库名。

## 为什么要做

生成器能校验结构，不能替团队决定领域边界；错误边界会让 Agent 在正确工具上做错误事情。

## 操作步骤

填写 domain、services、worktree；确保 id、repository、mount_path 唯一；至少设置一个 read-only。

## 关键文件解析

`access` 是研发合同，`fetch_mode` 是本地工作方式，两者不可混为一谈。

## 设计取舍

worktree 用于正常隔离研发；symlink 观察现有 checkout；copy 只适合教学副本。

## 验证命令与预期结果

运行 `python3 -m central_repo_scaffold inspect --config examples/domain.yaml` 与 `python3 -m central_repo_scaffold validate --config examples/domain.yaml`。

## 常见错误及根因

路径逃逸、重复 id、空验证命令会被拒绝；根因是输入合同不确定会扩散到文件和 Git 操作。

## 学员练习

故意制造一个重复 id 和一个 `../escape`，阅读精确错误路径后恢复。

## 完成标准

YAML 通过结构校验，并由学员解释每个服务的访问与模式。

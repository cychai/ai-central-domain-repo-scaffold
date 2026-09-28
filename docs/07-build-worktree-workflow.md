# 构建 Worktree 工作流

## 本节目标

理解并实现需求级中央 worktree 与服务仓按需挂载。

## 前置输入

中央仓和 worktree 模式服务仓都必须有 committed HEAD。

## 为什么要做

一个目录同时承载多个需求会发生分支和服务挂载冲突；两级 worktree 把需求上下文与各服务历史隔离。

## 操作步骤

先初始化并提交；再 `make dev-create BRANCH=feat/example`；进入新目录设置服务路径环境变量并初始化目标服务。

## 关键文件解析

`scripts/dev-worktree.py` 从 domain.yaml 解析选择器、模式和路径，完整预检后才创建。

## 设计取舍

不自动降级模式，不自动克隆，不强制删除分支；这些动作会掩盖根因或扩大影响面。

## 验证命令与预期结果

运行 `python3 -m central_repo_scaffold git-init --output /tmp/rendered-central`，再运行生成仓 `make dev-create BRANCH=feat/training`。

## 常见错误及根因

报 committed HEAD 缺失时应先创建提交或改清单决策；不能把失败补丁成静默 copy。

## 学员练习

为三个临时仓分别演示 worktree、symlink、copy，并解释差异。

## 完成标准

能创建和移除需求 worktree，服务挂载与 YAML 一致。

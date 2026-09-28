# 初始化 Git 与首个提交

## 本节目标

理解首个提交为何是 worktree 的结构前提。

## 前置输入

已渲染且通过无 Git 结构校验的目录；本机已有 Git 身份。

## 为什么要做

Git worktree 必须指向提交；只有 `git init` 没有 HEAD，无法成为可重复的需求基线。

## 操作步骤

检查 user.name/user.email；运行 git-init；检查分支、提交数和工作区状态。

## 关键文件解析

git-init 在提交前更新首次验证报告，使提交内容描述真实状态。

## 设计取舍

生成器不写全局 Git 身份；身份缺失必须由操作者处理。

## 验证命令与预期结果

运行 `git -C /tmp/rendered-central rev-list --count HEAD`，预期为 1；`git status --short` 为空。

## 常见错误及根因

No commits yet 不是 worktree 脚本故障；根因是缺少 committed HEAD。

## 学员练习

在隔离 HOME 中复现身份缺失，确认目标不被半初始化。

## 完成标准

仓库有正确默认分支、恰好一个首个提交和干净状态。

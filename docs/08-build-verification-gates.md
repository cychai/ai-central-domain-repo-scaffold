# 构建验证门禁

## 本节目标

建立结构、Git、挂载和证据状态校验。

## 前置输入

已有可渲染中央仓和 worktree 脚本。

## 为什么要做

“文件存在”不等于“仓库可用”；门禁需要逐层验证配置、结构、Git 和服务状态。

## 操作步骤

编写 verify-central.py 检查关键文件、路径和 committed HEAD；把服务验证保持为显式动作。

## 关键文件解析

验证器只检查它能证明的事实，不按技术栈猜测额外命令。

## 设计取舍

首次生成不运行服务仓验证，因此 build-record 必须写 not-executed。

## 验证命令与预期结果

运行 `python3 -m central_repo_scaffold verify --output /tmp/rendered-central --require-git` 和生成仓 `make verify`。

## 常见错误及根因

把未执行写成 passed 会破坏证据链；根因是混淆“应该通过”和“已经证明”。

## 学员练习

删除一个临时副本中的关键文档，观察门禁失败后恢复。

## 完成标准

验证失败能定位层级，成功状态都有实际命令证据。

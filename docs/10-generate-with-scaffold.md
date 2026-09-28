# 使用分阶段与一键生成器

## 本节目标

把手工判断映射到每个自动化阶段。

## 前置输入

已完成手工路径并安装脚手架依赖。

## 为什么要做

阶段化命令让输入错误、渲染错误、Git 错误和验证错误各自可定位；create 只负责编排。

## 操作步骤

依次执行 inspect、validate、plan、render、git-init、verify；再换路径执行 create。

## 关键文件解析

CLI 对应 config、generator、git、verification 和 stages 模块，职责不交叉。

## 设计取舍

真实领域先走 plan 审阅；只有输入确认后才运行 create。

## 验证命令与预期结果

运行 `python3 -m central_repo_scaffold create --config examples/domain.yaml --output /tmp/generated-central`。

## 常见错误及根因

重复使用已存在输出会失败；根因是工具拒绝不安全覆盖，不应增加 force 绕过。

## 学员练习

记录每个阶段的输入、输出、是否写文件和失败恢复点。

## 完成标准

分阶段与 create 都生成一个可验证、单提交中央仓。

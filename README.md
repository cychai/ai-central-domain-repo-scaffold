# 中央领域仓通用脚手架

从多服务 YAML 清单生成可工作的中央领域仓，并通过手工构建、分阶段生成和一键生成三条路径讲清楚每个设计决策。

## 环境

- Python 3.11+
- Git 2.28+
- GNU Make
- 已配置 Git `user.name` 与 `user.email`（创建首个提交需要）

```bash
make install
make test
make verify
```

`make install` 创建本地 `.venv`，不修改全局 Python 环境。若依赖安装失败，先检查 Python、网络或包源，再重试；不要绕过依赖检查。
如果系统默认 `python3` 低于 3.11，显式指定新版本：

```bash
make install BOOTSTRAP_PYTHON=/path/to/python3.11
```

## 三条路径

- 手工构建：从 [`docs/00-training-overview.md`](docs/00-training-overview.md) 开始，逐章完成领域分析、文档、worktree、验证和 Git 初始化。
- 分阶段生成：依次运行 `inspect`、`validate`、`plan`、`render`、`git-init`、`verify`，观察每一层职责。
- 一键生成：确认配置后运行 `create`，用于迁移到真实领域。

```bash
.venv/bin/python -m central_repo_scaffold inspect --config examples/domain.yaml
.venv/bin/python -m central_repo_scaffold validate --config examples/domain.yaml
.venv/bin/python -m central_repo_scaffold plan --config examples/domain.yaml --output /tmp/order-domain
.venv/bin/python -m central_repo_scaffold create --config examples/domain.yaml --output /tmp/order-domain
```

也可以直接生成完整示例：

```bash
make example OUTPUT=/tmp/order-fulfillment-central-domain
```

## 安全边界

- 目标目录存在时拒绝覆盖。
- 生成阶段不克隆、不挂载、不修改服务仓。
- 本地服务仓路径只通过环境变量提供，不进入版本控制。
- 不修改全局 Git 配置；Git 身份缺失时明确失败。
- 服务验证命令不会在生成阶段自动执行，初始状态为 `not-executed`。

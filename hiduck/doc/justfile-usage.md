# justfile 使用指南

项目使用 `justfile` 统一封装常用的 `uv`、Uvicorn 和 Alembic 命令。所有命令均在项目根目录执行。

## 环境准备

### 安装 uv

项目使用 `uv` 管理 Python、虚拟环境和依赖。Linux 或 macOS 可以使用官方安装脚本：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

安装完成后重新打开终端，并检查命令是否可用：

```bash
uv --version
```

其他安装方式参见 [uv 官方安装文档](https://docs.astral.sh/uv/getting-started/installation/)。

### 安装 just

使用 `uv` 安装 `just` 命令：

```bash
uv tool install rust-just
```

安装完成后检查命令是否可用：

```bash
just --version
```

如果需要使用其他包管理器，参见 [just 官方安装文档](https://just.systems/man/en/packages.html)。

### 准备 Python 与项目依赖

项目要求 Python 3.13。安装对应版本并同步虚拟环境与依赖：

```bash
uv python install 3.13
just sync
```

`just sync` 执行底层命令 `uv sync`。

### 准备环境变量

首次运行且项目根目录不存在 `.env` 时，复制配置模板：

```bash
cp .env.example .env
```

随后在 `.env` 中填写实际环境的数据库配置。`APP_DATABASE_USER` 和 `APP_DATABASE_PASSWORD` 为必填项；数据库地址、端口和数据库名按实际环境调整。禁止将包含真实凭据的 `.env` 提交到版本库。

## 命令说明

### 查看命令

```bash
just
```

列出当前 `justfile` 中支持的全部命令。

### 同步项目环境

```bash
just sync
```

同步项目要求的 Python 版本、`.venv` 虚拟环境及 `uv.lock` 中的依赖。

### 启动开发服务

```bash
just run
```

以热重载方式启动 `main:app`。服务会持续运行，按 `Ctrl+C` 停止。

### 生成迁移文件

```bash
just revision "创建用户表"
```

该命令会连接 `.env` 指向的数据库，对比数据库结构与 SQLAlchemy 模型，并在 `alembic/versions` 下生成迁移文件，但不会应用迁移。生成后需要检查迁移文件内容。

### 升级数据库

```bash
just upgrade
```

该命令会连接 `.env` 指向的数据库，并执行尚未应用的迁移直到 `head`。执行前需要确认目标数据库和迁移内容。

### 回退数据库

默认回退一个迁移版本：

```bash
just downgrade
```

也可以指定目标版本：

```bash
just downgrade <revision>
```

该命令会修改 `.env` 指向的数据库。执行前需要确认目标数据库、目标版本以及迁移文件中的 `downgrade` 实现。

### 查看迁移历史

```bash
just history
```

显示项目本地迁移脚本的版本历史，不修改数据库。

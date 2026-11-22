# FastAPI Custom Template

基于 Python 3.13 和 FastAPI 的服务端项目模板，支持 MySQL 异步访问及 Celery 异步任务。

## 项目特性

- FastAPI 提供异步 HTTP 接口与 OpenAPI 文档。
- SQLAlchemy 2.0 与 asyncmy 提供 MySQL 异步访问，Alembic 支持数据库迁移。
- Celery 与 RabbitMQ 支持异步任务投递和消费，内置 ping 示例。
- 统一接口响应、全局异常处理与异常堆栈日志。
- 日志同时输出到终端及 `log/general.jsonl`。
- 支持根目录 `.env` 配置和 CORS。

## 环境准备

需要 Python 3.13、`uv`、MySQL 和 RabbitMQ。以下命令均在仓库根目录执行。

安装项目依赖：

```bash
uv sync
```

首次使用时复制配置模板；已有 `.env` 时只补齐新增配置项：

```bash
cp .env.example .env
```

编辑 `.env`，配置 MySQL 和 RabbitMQ 的地址、端口、数据库名称及 virtual host，并填写
`APP_DATABASE_USER`、`APP_DATABASE_PASSWORD`、`APP_RABBITMQ_USERNAME`、`APP_RABBITMQ_PASSWORD`。
API 与 Worker 都需要这些配置。RabbitMQ 账号须具备目标 virtual host 的配置、读和写权限。

## 启动服务

API 和 Worker 分别在不同终端运行。

启动 API 开发服务：

```bash
uv run uvicorn main:app --reload
```

启动 Worker：

```bash
uv run celery -A celery_worker:celery_app worker --queues=template.ping --concurrency=1 --loglevel=INFO
```

已安装 `just` 时，也可使用 `just run` 和 `just worker`。

API 启动时会自动声明 RabbitMQ 交换机、队列及绑定，RabbitMQ 必须可连接。
MySQL 不可用时应用仍可启动，健康检查返回 `503`。

服务启动后可访问：

- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- MySQL 健康检查：`http://127.0.0.1:8000/api/v1/health`
- 异步 ping 接口：`POST http://127.0.0.1:8000/api/v1/tasks/ping`

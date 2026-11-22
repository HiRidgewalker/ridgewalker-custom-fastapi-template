# FastAPI Custom Template

基于 Python 3.13、FastAPI、SQLAlchemy 2.0、MySQL 异步驱动和 Celery 的分层项目模板，使用 RabbitMQ 投递异步任务。

## 初始化环境

项目统一使用 `uv` 管理 Python 和依赖：

```bash
uv sync
```

首次使用时复制配置模板；已有 `.env` 时只补齐新增配置项：

```bash
cp .env.example .env
```

`APP_DATABASE_USER`、`APP_DATABASE_PASSWORD`、`APP_RABBITMQ_USERNAME` 和
`APP_RABBITMQ_PASSWORD` 必须填写。API 与 Worker 共用 `Settings`，两种进程都需要这些配置。
数据库连接超时通过 `APP_DATABASE_CONNECT_TIMEOUT_SECONDS` 配置，CORS 配置使用 JSON 数组格式。

运行前需要准备可连接的 RabbitMQ，账号须具备目标 virtual host 的配置、读和写权限。
RabbitMQ 配置均从根目录 `.env` 由 `Settings` 统一加载：

| 配置键 | 默认值或要求 |
| --- | --- |
| `APP_RABBITMQ_HOST` | `127.0.0.1` |
| `APP_RABBITMQ_PORT` | `5672` |
| `APP_RABBITMQ_USERNAME` | 必填，模板留空 |
| `APP_RABBITMQ_PASSWORD` | 必填，模板留空 |
| `APP_RABBITMQ_VIRTUAL_HOST` | `/` |
| `APP_RABBITMQ_CONNECT_TIMEOUT_SECONDS` | `5` 秒 |

用户名、密码和 virtual host 中的特殊字符由 Client 构造连接串时转义，`.env` 中填写原始值。
连接和消息发布最多重试 3 次；任务处理本身不做自动重试。

## 启动服务

以下命令都在仓库根目录执行，API 和 Worker 分别在不同终端运行。

API 启动时会声明 RabbitMQ 交换机、队列及绑定；也可先独立声明，重复执行不会清空队列：

```bash
uv run python -m src.client.celery_client.celery_topology
```

启动 API：

```bash
uv run uvicorn main:app --reload
```

启动 Worker：

```bash
uv run celery -A celery_worker:celery_app worker --queues=template.ping --concurrency=1 --loglevel=INFO
```

也可分别使用 `just topology`、`just run` 和 `just worker`。

服务启动后可访问：

- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- MySQL 健康检查：`http://127.0.0.1:8000/api/v1/health`
- 异步 ping 投递：`POST http://127.0.0.1:8000/api/v1/tasks/ping`

健康检查会执行 `SELECT 1`。MySQL 不可用时健康检查返回 `503`，应用仍可启动。
RabbitMQ 配置缺失或启动时队列无法声明会阻止 API 启动。Worker 可独立启动，并会声明自己消费的已定义队列。

## 投递异步任务

```bash
curl -i 'http://127.0.0.1:8000/api/v1/tasks/ping' \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello celery"}'
```

成功时返回 HTTP `202`：

```json
{
  "code": 202,
  "msg": "任务已投递",
  "data": {
    "task_id": "b462914a-8fb5-4f4f-b123-1cb25daefb6a"
  }
}
```

`message` 必须为去除首尾空白后非空的字符串，请求不接受额外字段。此接口沿用数据库会话依赖，但不读写数据库。

`task_id` 用于关联发布与消费日志。HTTP `202` 表示投递调用成功，Worker 是否完成处理需查看其终端中的
`celery ping received` 日志，或项目下的 `log/general.jsonl`，确认任务 ID 与响应一致。Worker 未启动时消息会等待消费。
示例关闭结果保存，不提供任务状态查询或结果后端。

| 现象 | 定位方式 |
| --- | --- |
| 配置校验失败 | 检查必填凭据、端口和连接超时 |
| API 启动失败并提示声明拓扑失败 | 检查 RabbitMQ 地址、virtual host 和账号权限 |
| 投递接口返回 `422` | 检查 `message` 类型、空白内容及额外字段 |
| 投递接口返回 `503` | 检查运行期间的 RabbitMQ 连接和队列权限 |
| 投递成功但无消费日志 | 确认 Worker 正在消费 `template.ping`，并查看其启动和任务失败日志 |

## 响应结构

接口统一返回 `ResponseSchema[业务 Schema]`，`code` 与实际 HTTP 状态码一致。普通成功响应为：

```json
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

业务 Schema 中的 `datetime` 字段按 ISO 8601 格式输出。路由不存在、请求字段校验失败、项目自定义异常与未知异常也使用相同结构，其中请求字段校验失败的 `data` 会列出字段位置、原因和错误类型。

## 分层约束

业务调用方向固定为 `controller`、`service`、`dao`。数据库会话由 `client` 层统一创建，Controller 通过 `DBSessionDependency` 注入 `db_session` 后显式传给 Service，Service 再按需传给 DAO。事务提交和回滚由会话上下文统一管理。

Celery 配置、拓扑及发布封装位于 `src/client/celery_client/`。HTTP Service 在线程中调用同步 Publisher，
避免阻塞事件循环；`celery_worker.py` 仅注册同步任务、校验消息并调用异步 Service。当前任务只写日志，
不访问异步数据库或复用跨事件循环的连接池。

新增任务时依次完成：

1. 在 `src/schema/` 定义请求与响应模型，在 `src/service/` 实现投递编排和任务处理。
2. 在 `src/client/celery_client/celery_task_definition.py` 增加任务名称、独立队列与 routing key，并将它们加入 `task_queues` 和 `task_routes`。不要复用 `template.ping` 来承载其他任务，也不要修改默认队列借用路由。
3. 在 `celery_worker.py` 增加薄任务适配入口，装饰器名称与任务定义一致，参数沿用 `raw_payload` JSON 约定；处理失败时在 Worker 入口记录一次异常并重新抛出。
4. 按需在 `src/controller/` 增加端点并汇总到 `router.py`，Service 通过 `CeleryPublisher.publish_task` 发布消息，仅向上返回业务 Schema。
5. 执行拓扑声明命令并重启 API 和 Worker；如新增独立消费队列，启动相应 Worker 时在 `--queues` 中指定。

任务导入由 `TASK_IMPORTS` 集中指定，目前为 `celery_worker`。程序导入时不连接 RabbitMQ，实际连接发生在队列声明、发布或 Worker 启动时。

# FastAPI Custom Template

基于 Python 3.13、FastAPI、SQLAlchemy 2.0 和 MySQL 异步驱动的分层项目模板。

## 初始化环境

项目统一使用 `uv` 管理 Python 和依赖：

```bash
uv sync
```

复制配置模板并填写 MySQL 登录信息：

```bash
cp .env.example .env
```

`APP_DATABASE_USER` 和 `APP_DATABASE_PASSWORD` 必须填写。数据库连接超时通过
`APP_DATABASE_CONNECT_TIMEOUT_SECONDS` 配置，CORS 配置使用 JSON 数组格式。

## 启动服务

```bash
uv run uvicorn main:app --reload
```

服务启动后可访问：

- OpenAPI 文档：`http://127.0.0.1:8000/docs`
- MySQL 健康检查：`http://127.0.0.1:8000/api/v1/health`

健康检查会执行 `SELECT 1`。MySQL 不可用时接口返回 `503`，应用本身仍可启动。

## 分层约束

业务调用方向固定为 `controller`、`service`、`dao`。数据库会话由 `client` 层统一创建，Controller 通过 `DBSessionDependency` 注入 `db_session` 后显式传给 Service，Service 再按需传给 DAO。事务提交和回滚由会话上下文统一管理。

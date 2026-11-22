# 列出项目支持的命令。
default:
    @just --list

# 同步 Python 版本、虚拟环境和项目依赖。
sync:
    uv sync

# 以热重载方式启动 FastAPI 开发服务。
run:
    uv run uvicorn main:app --reload

# 向 RabbitMQ 声明交换机、队列和绑定。
topology:
    uv run python -m src.client.celery_client.celery_topology

# 启动异步 ping Worker，只消费 template.ping。
worker:
    uv run celery -A celery_worker:celery_app worker --queues=template.ping --concurrency=1 --loglevel=INFO

# 根据当前模型与数据库结构生成迁移文件。
revision $MESSAGE:
    uv run alembic revision --autogenerate -m "$MESSAGE"

# 将数据库升级到最新迁移版本。
upgrade:
    uv run alembic upgrade head

# 回退数据库迁移，默认回退一个版本。
downgrade $REVISION="-1":
    uv run alembic downgrade "$REVISION"

# 查看迁移历史。
history:
    uv run alembic history

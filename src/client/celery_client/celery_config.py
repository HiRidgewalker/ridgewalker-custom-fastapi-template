"""创建 API 与 Worker 共用的 Celery 应用。"""

from urllib.parse import quote

from celery import Celery

from src.client.celery_client.celery_task_definition import (
    PING_TASK_NAME,
    TASK_EXCHANGE_NAME,
    TASK_IMPORTS,
    task_queues,
    task_routes,
)
from src.core.config import settings

BROKER_MAX_RETRIES = 3
PUBLISH_MAX_RETRIES = 3


def _broker_url() -> str:
    username = quote(settings.rabbitmq_username, safe="")
    password = quote(settings.rabbitmq_password.get_secret_value(), safe="")
    virtual_host = quote(settings.rabbitmq_virtual_host, safe="")
    return (
        f"amqp://{username}:{password}"
        f"@{settings.rabbitmq_host}:{settings.rabbitmq_port}/{virtual_host}"
    )


def create_celery_app() -> Celery:
    """构造尚未连接 RabbitMQ 的 Celery 应用。"""
    application = Celery("fastapi_template", broker=_broker_url())
    application.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        task_ignore_result=True,
        task_create_missing_queues=False,
        task_default_queue=PING_TASK_NAME,
        task_default_exchange=TASK_EXCHANGE_NAME,
        task_default_exchange_type="direct",
        task_default_routing_key=PING_TASK_NAME,
        task_queues=task_queues,
        task_routes=task_routes,
        imports=TASK_IMPORTS,
        worker_prefetch_multiplier=1,
        broker_connection_timeout=settings.rabbitmq_connect_timeout_seconds,
        broker_connection_retry_on_startup=True,
        broker_connection_max_retries=BROKER_MAX_RETRIES,
        task_publish_retry=True,
        task_publish_retry_policy={
            "max_retries": PUBLISH_MAX_RETRIES,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 1,
        },
    )
    return application


celery_app = create_celery_app()


def close_celery() -> None:
    """关闭本进程持有的 Celery 应用资源。"""
    celery_app.close()

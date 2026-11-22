"""提供 Celery CLI 加载的 Worker 任务适配入口。"""

import asyncio

from celery import Task

from src.client.celery_client.celery_config import celery_app
from src.client.celery_client.celery_task_definition import PING_TASK_NAME
from src.schema.celery_ping_schema import PingCreate
from src.service.celery_ping_service import CeleryPingService
from src.util.log_util import general_logger


@celery_app.task(bind=True, name=PING_TASK_NAME)
def ping_task(self: Task, raw_payload: dict[str, object]) -> None:
    """校验队列消息并执行异步 ping 服务。"""
    task_id = str(self.request.id)
    try:
        payload = PingCreate.model_validate(raw_payload)
        asyncio.run(CeleryPingService.execute_ping(payload, task_id))
    except Exception:
        general_logger.exception(
            "celery ping failed",
            extra={"data": {"task_id": task_id}},
        )
        raise

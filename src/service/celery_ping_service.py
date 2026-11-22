import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.client.celery_client.celery_publisher import CeleryPublisher
from src.client.celery_client.celery_task_definition import PING_TASK_NAME
from src.schema.celery_ping_schema import PingCreate, PingRead
from src.util.log_util import general_logger


class CeleryPingService:
    """编排 ping 消息投递及 Worker 消费。"""

    @staticmethod
    async def enqueue_ping(
        db_session: AsyncSession,
        payload: PingCreate,
    ) -> PingRead:
        """沿用接口会话契约并投递消息，当前示例不访问数据库。"""
        task_id = await asyncio.to_thread(
            CeleryPublisher.publish_task,
            PING_TASK_NAME,
            payload,
        )
        general_logger.info(
            "celery ping enqueued",
            extra={"data": {"task_id": task_id}},
        )
        return PingRead(task_id=task_id)

    @staticmethod
    async def execute_ping(payload: PingCreate, task_id: str) -> None:
        """记录消息执行结果，供调用方按任务标识查看。"""
        general_logger.info(
            "celery ping received",
            extra={"data": {"task_id": task_id, "message": payload.message}},
        )

"""封装同步任务发布及外部异常转换。"""

from amqp.exceptions import AMQPError
from celery.exceptions import CeleryError
from kombu.exceptions import KombuError
from pydantic import BaseModel

from src.client.celery_client.celery_config import celery_app
from src.core.constants import SERVICE_UNAVAILABLE_CODE
from src.core.exception import CeleryException


class CeleryPublisher:
    """按任务名称发布经过 Schema 校验的 JSON 消息。"""

    @staticmethod
    def publish_task(task_name: str, payload: BaseModel) -> str:
        """在有限重试后发布消息，仅返回任务标识。"""
        raw_payload = payload.model_dump(mode="json")
        try:
            with celery_app.connection_for_write() as connection:
                connection.ensure_connection(
                    max_retries=celery_app.conf.broker_connection_max_retries,
                )
                result = celery_app.send_task(
                    task_name,
                    kwargs={"raw_payload": raw_payload},
                    connection=connection,
                    ignore_result=True,
                )
        except (KombuError, CeleryError, AMQPError, OSError) as exc:
            raise CeleryException(
                code=SERVICE_UNAVAILABLE_CODE,
                message=f"发布 Celery 任务失败: task_name={task_name}",
            ) from exc
        return str(result.id)

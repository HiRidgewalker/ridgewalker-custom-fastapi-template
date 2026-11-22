"""声明 RabbitMQ 交换机、队列与绑定。"""

from amqp.exceptions import AMQPError
from celery.exceptions import CeleryError
from kombu.exceptions import KombuError

from src.client.celery_client.celery_config import celery_app, close_celery
from src.client.celery_client.celery_task_definition import (
    TASK_EXCHANGE_NAME,
    task_queues,
)
from src.core.constants import SERVICE_UNAVAILABLE_CODE
from src.core.exception import CeleryException


def declare_topology() -> None:
    """在有限连接重试后声明可重复创建的 RabbitMQ 拓扑。"""
    try:
        with celery_app.connection_for_write() as connection:
            connection.ensure_connection(
                max_retries=celery_app.conf.broker_connection_max_retries,
            )
            channel = connection.channel()
            try:
                for queue in task_queues:
                    queue(channel).declare()
            finally:
                channel.close()
    except (KombuError, CeleryError, AMQPError, OSError) as exc:
        queue_names = ",".join(queue.name for queue in task_queues)
        raise CeleryException(
            code=SERVICE_UNAVAILABLE_CODE,
            message=(
                f"声明 RabbitMQ 拓扑失败: exchange={TASK_EXCHANGE_NAME}, "
                f"queues={queue_names}"
            ),
        ) from exc


def main() -> None:
    """声明任务队列并释放本次命令的 Celery 资源。"""
    try:
        declare_topology()
    finally:
        close_celery()


if __name__ == "__main__":
    main()

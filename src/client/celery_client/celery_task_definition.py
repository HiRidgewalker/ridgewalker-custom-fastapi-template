"""集中声明任务名称、队列路由和 Worker 任务导入。"""

from kombu import Exchange, Queue

TASK_EXCHANGE_NAME = "template"
PING_TASK_NAME = "template.ping"
TASK_IMPORTS = ("celery_worker",)

task_exchange = Exchange(TASK_EXCHANGE_NAME, type="direct", durable=True)
task_queues = (
    Queue(
        PING_TASK_NAME,
        exchange=task_exchange,
        routing_key=PING_TASK_NAME,
        durable=True,
    ),
)
task_routes = {
    PING_TASK_NAME: {
        "queue": PING_TASK_NAME,
        "routing_key": PING_TASK_NAME,
    },
}

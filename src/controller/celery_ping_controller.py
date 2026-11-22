from fastapi import APIRouter

from src.client.database_client import DBSessionDependency
from src.core.constants import ACCEPTED_CODE
from src.schema.celery_ping_schema import PingCreate, PingRead
from src.schema.response_schema import ResponseSchema
from src.service.celery_ping_service import CeleryPingService

router = APIRouter(prefix="/tasks", tags=["tasks"])


class CeleryPingController:
    """提供 Celery 异步消息投递端点。"""

    @staticmethod
    @router.post("/ping", status_code=ACCEPTED_CODE)
    async def enqueue_ping(
        payload: PingCreate,
        db_session: DBSessionDependency,
    ) -> ResponseSchema[PingRead]:
        """投递 ping 消息并返回任务标识。"""
        result = await CeleryPingService.enqueue_ping(db_session, payload)
        return ResponseSchema[PingRead](
            code=ACCEPTED_CODE,
            msg="任务已投递",
            data=result,
        )

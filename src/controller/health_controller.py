from fastapi import APIRouter

from src.client.database_client import DBSessionDependency
from src.core.constants import SUCCESS_CODE
from src.schema.health_schema import HealthRead
from src.schema.response_schema import ResponseSchema
from src.service.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


class HealthController:
    """提供服务健康检查端点。"""

    @staticmethod
    @router.get("")
    async def get_health(
        db_session: DBSessionDependency,
    ) -> ResponseSchema[HealthRead]:
        """检查应用连接的 MySQL 是否可用。"""
        health = await HealthService.check_health(db_session)
        return ResponseSchema[HealthRead](
            code=SUCCESS_CODE,
            msg="success",
            data=health,
        )

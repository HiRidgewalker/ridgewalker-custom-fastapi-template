from fastapi import APIRouter

from src.client.database_client import DBSessionDependency
from src.schema.health_schema import HealthRead
from src.service.health_service import HealthService

router = APIRouter(prefix="/health", tags=["health"])


class HealthController:
    """提供服务健康检查端点。"""

    @staticmethod
    @router.get("")
    async def get_health(db_session: DBSessionDependency) -> HealthRead:
        """检查应用连接的 MySQL 是否可用。"""
        return await HealthService.check_health(db_session)

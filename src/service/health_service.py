from src.client.database_client import SessionDep
from src.core.exception import DatabaseError
from src.dao.health_dao import HealthDao
from src.schema.health_schema import HealthRead


class HealthService:
    """编排服务健康状态检查。"""

    def __init__(self, health_dao: HealthDao) -> None:
        self._health_dao = health_dao

    async def check_health(self) -> HealthRead:
        """检查数据库并返回服务健康状态。"""
        is_available = await self._health_dao.is_database_available()
        if not is_available:
            raise DatabaseError("MySQL 健康检查未返回预期结果")

        return HealthRead(status="ok")


def get_health_service(session: SessionDep) -> HealthService:
    """使用当前事务会话创建健康检查 Service。"""
    return HealthService(HealthDao(session))

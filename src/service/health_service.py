from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import SERVICE_UNAVAILABLE_CODE
from src.core.exception import DatabaseException
from src.dao.health_dao import HealthDao
from src.schema.health_schema import HealthRead


class HealthService:
    """编排服务健康状态检查。"""

    @staticmethod
    async def check_health(db_session: AsyncSession) -> HealthRead:
        """检查数据库并返回服务健康状态。"""
        is_available = await HealthDao.is_database_available(db_session)
        if not is_available:
            raise DatabaseException(
                code=SERVICE_UNAVAILABLE_CODE,
                message="MySQL 健康检查未返回预期结果",
            )

        return HealthRead(status="ok")

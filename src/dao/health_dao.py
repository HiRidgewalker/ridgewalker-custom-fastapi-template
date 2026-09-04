from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.constants import SERVICE_UNAVAILABLE_CODE
from src.core.exception import DatabaseException


class HealthDao:
    """执行数据库健康检查语句。"""

    @staticmethod
    async def is_database_available(db_session: AsyncSession) -> bool:
        """执行轻量查询并判断 MySQL 是否正常响应。"""
        try:
            result = await db_session.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise DatabaseException(
                code=SERVICE_UNAVAILABLE_CODE,
                message="MySQL 健康检查执行失败",
            ) from exc

        return result.scalar_one() == 1

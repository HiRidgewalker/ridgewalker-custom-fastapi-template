from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exception import DatabaseError


class HealthDao:
    """执行数据库健康检查语句。"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_database_available(self) -> bool:
        """执行轻量查询并判断 MySQL 是否正常响应。"""
        try:
            result = await self._session.execute(text("SELECT 1"))
        except SQLAlchemyError as exc:
            raise DatabaseError("MySQL 健康检查执行失败") from exc

        return result.scalar_one() == 1

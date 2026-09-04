from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import settings

database_url = URL.create(
    drivername="mysql+asyncmy",
    username=settings.database_user,
    password=settings.database_password.get_secret_value(),
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name,
)

database_engine = create_async_engine(
    database_url,
    connect_args={
        "connect_timeout": settings.database_connect_timeout_seconds,
    },
    pool_pre_ping=True,
)
transaction_session_maker = async_sessionmaker(
    bind=database_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_transaction_session() -> AsyncGenerator[AsyncSession, None]:
    """为单次请求提供自动提交或回滚的事务会话。"""
    async with transaction_session_maker.begin() as db_session:
        yield db_session


DBSessionDependency = Annotated[AsyncSession, Depends(get_transaction_session)]


async def close_database() -> None:
    """关闭数据库引擎持有的连接池。"""
    await database_engine.dispose()

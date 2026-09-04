from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.client.database_client import close_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """在应用退出时释放数据库连接池。"""
    try:
        yield
    finally:
        await close_database()

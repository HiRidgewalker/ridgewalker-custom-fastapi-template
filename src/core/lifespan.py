import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.client.celery_client.celery_config import close_celery
from src.client.celery_client.celery_topology import declare_topology
from src.client.database_client import close_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """启动时声明 RabbitMQ 拓扑，退出时释放 Celery 和数据库资源。"""
    try:
        await asyncio.to_thread(declare_topology)
        yield
    finally:
        try:
            await asyncio.to_thread(close_celery)
        finally:
            await close_database()

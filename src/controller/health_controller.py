from typing import Annotated

from fastapi import APIRouter, Depends

from src.schema.health_schema import HealthRead
from src.service.health_service import HealthService, get_health_service

router = APIRouter(prefix="/health", tags=["health"])

HealthServiceDep = Annotated[HealthService, Depends(get_health_service)]


class HealthController:
    """提供服务健康检查端点。"""

    @staticmethod
    @router.get("")
    async def get_health(service: HealthServiceDep) -> HealthRead:
        """检查应用连接的 MySQL 是否可用。"""
        return await service.check_health()

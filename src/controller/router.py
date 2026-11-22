from fastapi import APIRouter

from src.controller.celery_ping_controller import router as celery_ping_router
from src.controller.health_controller import router as health_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)
router.include_router(celery_ping_router)

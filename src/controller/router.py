from fastapi import APIRouter

from src.controller.health_controller import router as health_router

router = APIRouter(prefix="/api/v1")
router.include_router(health_router)

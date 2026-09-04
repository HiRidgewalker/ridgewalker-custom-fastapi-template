from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.controller.router import router
from src.core.access_log_middleware import AccessLogMiddleware
from src.core.config import settings
from src.core.exception_handler import register_exception_handlers
from src.core.lifespan import lifespan

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
app.add_middleware(AccessLogMiddleware)

app.include_router(router)

register_exception_handlers(app)

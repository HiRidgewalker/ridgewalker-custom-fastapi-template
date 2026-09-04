import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.exception import AppError

logger = logging.getLogger("app.exception")


async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
    """记录可预期异常并转换为 HTTP 响应。"""
    logger.warning(
        "application error",
        extra={"error_code": exc.code, "path": request.url.path},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message},
    )


async def handle_unknown_error(request: Request, exc: Exception) -> JSONResponse:
    """记录未知异常并返回不包含内部细节的 HTTP 响应。"""
    logger.exception(
        "unhandled application error",
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=500,
        content={
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务内部错误",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册全局异常处理器。"""
    app.add_exception_handler(AppError, handle_app_error)
    app.add_exception_handler(Exception, handle_unknown_error)

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.core.constants import INTERNAL_SERVER_ERROR_CODE
from src.core.exception import AppException

logger = logging.getLogger("app.exception")


async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
    """记录可预期异常并转换为 HTTP 响应。"""
    logger.warning(
        "application exception",
        extra={"error_code": exc.code, "path": request.url.path},
    )
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
    )


async def handle_unknown_error(request: Request, exc: Exception) -> JSONResponse:
    """记录未知异常并返回不包含内部细节的 HTTP 响应。"""
    logger.exception(
        "unhandled application error",
        extra={"path": request.url.path},
    )
    return JSONResponse(
        status_code=INTERNAL_SERVER_ERROR_CODE,
        content={
            "code": INTERNAL_SERVER_ERROR_CODE,
            "message": "服务内部错误",
            "data": {},
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册全局异常处理器。"""
    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(Exception, handle_unknown_error)

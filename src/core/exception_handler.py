from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.constants import (
    INTERNAL_SERVER_ERROR_CODE,
    NOT_FOUND_CODE,
    UNPROCESSABLE_ENTITY_CODE,
)
from src.core.exception import AppException
from src.schema.response_schema import ResponseSchema, ValidationErrorDetail
from src.util.log_util import general_logger


def _build_json_response(status_code: int, response: BaseModel) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(mode="json"),
    )


async def handle_app_exception(request: Request, exc: AppException) -> JSONResponse:
    """记录可预期异常并转换为 HTTP 响应。"""
    general_logger.exception(
        "application exception",
        exc_info=exc,
        extra={"data": {"error_code": exc.code, "path": request.url.path}},
    )
    response = ResponseSchema[dict[str, object]](
        code=exc.code,
        msg=exc.message,
        data=exc.data,
    )
    return _build_json_response(exc.code, response)


async def handle_http_exception(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """将路由不存在等 HTTP 异常转换为统一响应。"""
    is_route_not_found = exc.status_code == NOT_FOUND_CODE
    message = "请求路由不存在" if is_route_not_found else str(exc.detail)
    data = {"path": request.url.path} if is_route_not_found else {}
    general_logger.exception(
        "http exception",
        exc_info=exc,
        extra={"data": {"error_code": exc.status_code, "path": request.url.path}},
    )
    response = ResponseSchema[dict[str, object]](
        code=exc.status_code,
        msg=message,
        data=data,
    )
    return _build_json_response(exc.status_code, response)


async def handle_request_validation_exception(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """返回请求字段校验失败的具体位置与原因。"""
    error_details = [
        ValidationErrorDetail(
            location=list(error["loc"]),
            message=error["msg"],
            error_type=error["type"],
        )
        for error in exc.errors()
    ]
    general_logger.exception(
        "request validation exception",
        exc_info=exc,
        extra={
            "data": {
                "error_code": UNPROCESSABLE_ENTITY_CODE,
                "error_count": len(error_details),
                "path": request.url.path,
            },
        },
    )
    response = ResponseSchema[list[ValidationErrorDetail]](
        code=UNPROCESSABLE_ENTITY_CODE,
        msg="请求参数校验失败",
        data=error_details,
    )
    return _build_json_response(UNPROCESSABLE_ENTITY_CODE, response)


async def handle_unknown_error(request: Request, exc: Exception) -> JSONResponse:
    """记录未知异常并返回不包含内部细节的 HTTP 响应。"""
    general_logger.exception(
        "unhandled application error",
        exc_info=exc,
        extra={"data": {"path": request.url.path}},
    )
    response = ResponseSchema[dict[str, object]](
        code=INTERNAL_SERVER_ERROR_CODE,
        msg="服务内部错误",
        data={},
    )
    return _build_json_response(INTERNAL_SERVER_ERROR_CODE, response)


def register_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册全局异常处理器。"""
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(
        RequestValidationError,
        handle_request_validation_exception,
    )
    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(Exception, handle_unknown_error)

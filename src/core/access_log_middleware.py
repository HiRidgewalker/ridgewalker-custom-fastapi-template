from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from src.util.log_util import general_logger


class AccessLogMiddleware(BaseHTTPMiddleware):
    """统一记录 HTTP 请求的访问日志。"""

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """记录请求方法、路径、状态码和耗时。"""
        started_at = perf_counter()
        status_code = 500

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration_ms = round((perf_counter() - started_at) * 1000, 2)
            general_logger.info(
                "request completed",
                extra={
                    "data": {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": duration_ms,
                    },
                },
            )

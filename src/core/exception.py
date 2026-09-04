class AppError(Exception):
    """作为项目内可预期异常的统一基类。"""

    def __init__(self, code: str, message: str, status_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


class DatabaseError(AppError):
    """表示数据库连接或语句执行失败。"""

    def __init__(self, message: str) -> None:
        super().__init__(
            code="DATABASE_UNAVAILABLE",
            message=message,
            status_code=503,
        )

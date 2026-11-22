class AppException(Exception):
    """作为项目内可预期异常的统一基类。"""

    def __init__(
        self,
        code: int,
        message: str,
        data: dict[str, object] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = {} if data is None else data.copy()


class DatabaseException(AppException):
    """表示数据库连接或语句执行失败。"""


class CeleryException(AppException):
    """表示 RabbitMQ 连接、队列声明或任务投递失败。"""

from pydantic import BaseModel


class ResponseSchema[ResponseDataType](BaseModel):
    """描述接口统一响应结构。"""

    code: int
    msg: str
    data: ResponseDataType


class ValidationErrorDetail(BaseModel):
    """描述单个请求字段的校验错误。"""

    location: list[str | int]
    message: str
    error_type: str

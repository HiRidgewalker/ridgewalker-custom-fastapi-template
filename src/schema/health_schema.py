from typing import Literal

from pydantic import BaseModel


class HealthRead(BaseModel):
    """描述健康检查成功响应。"""

    status: Literal["ok"]

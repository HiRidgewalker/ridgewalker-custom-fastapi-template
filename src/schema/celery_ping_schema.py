from pydantic import BaseModel, ConfigDict, Field


class PingCreate(BaseModel):
    """校验待投递的 ping 消息。"""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    message: str = Field(strict=True, min_length=1)


class PingRead(BaseModel):
    """返回已投递消息的任务标识。"""

    task_id: str

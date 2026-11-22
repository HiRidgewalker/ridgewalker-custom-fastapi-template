from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """集中加载并校验根目录 `.env` 中的应用配置。"""

    app_name: str = "FastAPI Custom Template"
    debug: bool = False
    cors_allow_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )
    cors_allow_methods: list[str] = Field(
        default_factory=lambda: [
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ]
    )
    cors_allow_headers: list[str] = Field(
        default_factory=lambda: ["Accept", "Authorization", "Content-Type"]
    )
    database_host: str = "127.0.0.1"
    database_port: int = Field(default=3306, ge=1, le=65535)
    database_connect_timeout_seconds: int = Field(default=5, ge=1)
    database_name: str = "app"
    database_user: str = ""
    database_password: SecretStr = SecretStr("")
    rabbitmq_host: str = "127.0.0.1"
    rabbitmq_port: int = Field(default=5672, ge=1, le=65535)
    rabbitmq_username: str = ""
    rabbitmq_password: SecretStr = SecretStr("")
    rabbitmq_virtual_host: str = "/"
    rabbitmq_connect_timeout_seconds: int = Field(default=5, ge=1)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        extra="ignore",
        frozen=True,
        validate_default=True,
    )

    @field_validator("database_host", "database_name", "database_user")
    @classmethod
    def _validate_required_database_text(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("数据库配置不能为空")
        return stripped_value

    @field_validator("database_password")
    @classmethod
    def _validate_database_password(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value():
            raise ValueError("数据库密码不能为空")
        return value

    @field_validator("rabbitmq_host", "rabbitmq_username", "rabbitmq_virtual_host")
    @classmethod
    def _validate_required_rabbitmq_text(cls, value: str) -> str:
        stripped_value = value.strip()
        if not stripped_value:
            raise ValueError("RabbitMQ 配置不能为空")
        return stripped_value

    @field_validator("rabbitmq_password")
    @classmethod
    def _validate_rabbitmq_password(cls, value: SecretStr) -> SecretStr:
        if not value.get_secret_value():
            raise ValueError("RabbitMQ 密码不能为空")
        return value


settings = Settings()

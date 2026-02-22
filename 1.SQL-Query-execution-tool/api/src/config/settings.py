from functools import lru_cache
from typing import Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: Union[str, list[str]] = "http://localhost:3000"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> list[str]:
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return ["http://localhost:3000"]

    # Database
    db_type: str = "postgresql"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "chatdb"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_pool_size: int = 10
    postgres_max_overflow: int = 20

    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_db: str = "chatdb"
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_pool_size: int = 10
    mysql_max_overflow: int = 20

    sqlite_path: str = "./local.db"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_ttl_seconds: int = 3600

    # LLM
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.0

    # DeepAgent
    deepagent_max_iterations: int = 10
    deepagent_timeout_seconds: int = 120

    # JWT Auth
    auth_enabled: bool = False
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    admin_username: str = "admin"
    admin_password: str = "admin"

    @property
    def postgres_dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def mysql_dsn(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}"
        )

    @property
    def sqlite_dsn(self) -> str:
        return f"sqlite+aiosqlite:///{self.sqlite_path}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    return Settings()

import re
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def validate_db_schema_name(value: str | None) -> str | None:
    if value is None:
        return None
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", value):
        raise ValueError("DB_SCHEMA must be a lowercase PostgreSQL identifier")
    return value


class Settings(BaseSettings):
    app_env: str = "education"
    workspace_id: str = "sample"
    google_cloud_project: str | None = None
    firestore_database: str = "(default)"
    use_in_memory_repository: bool = False
    database_url: str | None = None
    db_schema: str | None = None
    cloud_sql_connection_name: str | None = None
    cloud_sql_db: str | None = None
    cloud_sql_user: str | None = None
    cloud_sql_password: str | None = None
    cloud_sql_host: str | None = None
    db_pool_size: int = 1
    db_max_overflow: int = 0
    db_pool_timeout: int = 10
    db_pool_recycle: int = 1800

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("db_schema")
    @classmethod
    def validate_db_schema(cls, value: str | None) -> str | None:
        return validate_db_schema_name(value)

    @model_validator(mode="after")
    def validate_runtime_database_settings(self) -> "Settings":
        if self.use_in_memory_repository:
            return self

        if self.app_env in {"education", "production"}:
            if not self.database_url:
                raise ValueError("DATABASE_URL must be configured for PostgreSQL runtime")
            if not self.db_schema:
                raise ValueError("DB_SCHEMA must be configured for PostgreSQL runtime")

        return self

    @field_validator("db_pool_size", "db_max_overflow", "db_pool_timeout", "db_pool_recycle")
    @classmethod
    def validate_non_negative_pool_settings(cls, value: int) -> int:
        if value < 0:
            raise ValueError("DB pool settings must be non-negative")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

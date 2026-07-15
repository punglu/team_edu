from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "education"
    workspace_id: str = "sample"
    google_cloud_project: str | None = None
    firestore_database: str = "(default)"
    use_in_memory_repository: bool = False
    database_url: str | None = None
    cloud_sql_connection_name: str | None = None
    cloud_sql_db: str | None = None
    cloud_sql_user: str | None = None
    cloud_sql_password: str | None = None
    cloud_sql_host: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


def build_database_url(settings: Settings) -> str | None:
    if settings.database_url:
        return settings.database_url

    if all(
        [
            settings.cloud_sql_host,
            settings.cloud_sql_db,
            settings.cloud_sql_user,
            settings.cloud_sql_password,
        ]
    ):
        return (
            f"postgresql+psycopg2://{settings.cloud_sql_user}:{settings.cloud_sql_password}"
            f"@{settings.cloud_sql_host}/{settings.cloud_sql_db}"
        )

    return None


def _postgresql_connect_args(database_url: str, schema: str | None) -> dict[str, str]:
    if schema is None or make_url(database_url).get_backend_name() != "postgresql":
        return {}
    return {"options": f"-csearch_path={schema}"}


def create_database_engine(settings: Settings) -> Engine:
    database_url = build_database_url(settings)
    if not database_url:
        raise RuntimeError("DATABASE_URL must be configured for PostgreSQL runtime")

    connect_args = _postgresql_connect_args(database_url, settings.db_schema)
    engine = create_engine(
        database_url,
        echo=False,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_pre_ping=True,
        pool_recycle=settings.db_pool_recycle,
        pool_use_lifo=True,
        connect_args=connect_args,
    )

    if settings.db_schema and make_url(database_url).get_backend_name() == "postgresql":
        schema = settings.db_schema

        @event.listens_for(engine, "checkout")
        def set_search_path_on_checkout(dbapi_connection, connection_record, connection_proxy) -> None:
            with dbapi_connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {schema}")

    return engine


@lru_cache
def get_engine() -> Engine:
    return create_database_engine(get_settings())


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)


def get_db_session() -> Generator[Session | None, None, None]:
    settings = get_settings()
    if settings.use_in_memory_repository:
        yield None
        return

    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()


def check_cloud_sql_connection(settings: Settings) -> dict[str, str]:
    try:
        engine = create_database_engine(settings)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1")).close()
        return {"status": "ok", "message": "Cloud SQL connection successful"}
    except Exception:
        return {"status": "error", "message": "Cloud SQL connection failed"}

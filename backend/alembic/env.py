from logging.config import fileConfig

from alembic import context
from sqlalchemy import text
from sqlalchemy.engine import Connection

from app.core.config import Settings, validate_db_schema_name
from app.core.database import build_database_url, create_database_engine
from app.db.base import Base
from app.features.projects import models as project_models  # noqa: F401


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_target_schema() -> str:
    x_args = context.get_x_argument(as_dictionary=True)
    schema = x_args.get("schema") or Settings().db_schema
    if not schema:
        raise RuntimeError("Alembic requires a target schema via DB_SCHEMA or -x schema=<name>")
    validated = validate_db_schema_name(schema)
    if not validated:
        raise RuntimeError("Alembic requires a target schema")
    return validated


def run_migrations_offline() -> None:
    settings = Settings()
    url = build_database_url(settings)
    schema = get_target_schema()
    if not url:
        raise RuntimeError("Alembic requires DATABASE_URL")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=schema,
    )

    with context.begin_transaction():
        context.run_migrations()


def configure_context(connection: Connection, schema: str) -> None:
    connection.execute(text(f"SET search_path TO {schema}"))
    connection.commit()
    connection.dialect.default_schema_name = schema
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        version_table_schema=schema,
    )


def run_migrations_online() -> None:
    settings = Settings()
    schema = get_target_schema()
    engine = create_database_engine(settings)

    with engine.connect() as connection:
        configure_context(connection, schema)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

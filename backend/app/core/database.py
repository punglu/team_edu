from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

from app.core.config import Settings


def get_cloud_sql_engine(settings: Settings):
    """Create SQLAlchemy engine for Cloud SQL."""
    connection_string = None

    if settings.database_url:
        connection_string = settings.database_url
    elif all([settings.cloud_sql_host, settings.cloud_sql_db,
              settings.cloud_sql_user, settings.cloud_sql_password]):
        connection_string = (
            f"mysql+pymysql://{settings.cloud_sql_user}:{settings.cloud_sql_password}"
            f"@{settings.cloud_sql_host}/{settings.cloud_sql_db}"
        )

    if not connection_string:
        return None

    engine = create_engine(
        connection_string,
        echo=False,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    return engine


def test_cloud_sql_connection(settings: Settings) -> dict:
    """Test Cloud SQL connection and return status."""
    if not settings.database_url and not all([settings.cloud_sql_host, settings.cloud_sql_db,
                                               settings.cloud_sql_user, settings.cloud_sql_password]):
        return {
            "status": "skipped",
            "message": "Cloud SQL credentials not configured",
        }

    try:
        engine = get_cloud_sql_engine(settings)
        if not engine:
            return {
                "status": "error",
                "message": "Failed to create engine",
            }

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.close()

        return {
            "status": "ok",
            "message": "Cloud SQL connection successful",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }

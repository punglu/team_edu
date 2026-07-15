from __future__ import annotations

import argparse
import os

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.core.config import Settings
from app.core.database import create_database_engine
from app.features.projects.models import MemberModel
from app.features.projects.repository import SAMPLE_MEMBERS
from scripts.migrate_schemas import ALLOWED_SCHEMAS, validate_schemas


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Seed baseline members into education schemas.")
    parser.add_argument(
        "--schemas",
        nargs="*",
        default=ALLOWED_SCHEMAS,
        help="Target schemas. Defaults to all 13 education schemas.",
    )
    return parser.parse_args()


def build_settings(schema: str) -> Settings:
    return Settings(
        _env_file=None,
        app_env=os.getenv("APP_ENV", "education"),
        use_in_memory_repository=False,
        database_url=os.environ.get("DATABASE_URL"),
        db_schema=schema,
        cloud_sql_connection_name=os.environ.get("CLOUD_SQL_CONNECTION_NAME"),
        cloud_sql_db=os.environ.get("CLOUD_SQL_DB"),
        cloud_sql_user=os.environ.get("CLOUD_SQL_USER"),
        cloud_sql_password=os.environ.get("CLOUD_SQL_PASSWORD"),
        cloud_sql_host=os.environ.get("CLOUD_SQL_HOST"),
    )


def seed_schema(schema: str) -> int:
    settings = build_settings(schema)
    engine = create_database_engine(settings)
    base_insert = insert(MemberModel)
    stmt = base_insert.values(
        [
            {
                "id": member.id,
                "name": member.name,
                "department": member.department,
                "role": member.role,
                "active": member.active,
            }
            for member in SAMPLE_MEMBERS
        ]
    ).on_conflict_do_update(
        index_elements=[MemberModel.id],
        set_={
            "name": base_insert.excluded.name,
            "department": base_insert.excluded.department,
            "role": base_insert.excluded.role,
            "active": base_insert.excluded.active,
        },
    )
    with engine.begin() as connection:
        connection.execute(text(f"SET LOCAL search_path TO {schema}"))
        result = connection.execute(stmt)
    engine.dispose()
    return result.rowcount or 0


def main() -> int:
    args = parse_args()
    validate_schemas(args.schemas)

    for schema in args.schemas:
        print(f"[{schema}] members_seeded={seed_schema(schema)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

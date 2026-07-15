from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect, text

from app.core.config import get_settings
from app.core.database import get_engine, get_session_factory
from app.main import app


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
BACKEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_TABLES = {"projects", "project_invited_members", "members", "alembic_version"}


def _require_test_database_url() -> str:
    if not TEST_DATABASE_URL:
        pytest.skip("TEST_DATABASE_URL is not configured")
    return TEST_DATABASE_URL


def _run_alembic(schema: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = _require_test_database_url()
    env["APP_ENV"] = "test"
    command = [
        sys.executable,
        "-m",
        "alembic",
        "-c",
        "alembic.ini",
        "-x",
        f"schema={schema}",
        *args,
    ]
    return subprocess.run(
        command,
        cwd=BACKEND_DIR,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _configure_runtime(schema: str) -> None:
    os.environ["APP_ENV"] = "test"
    os.environ["DATABASE_URL"] = _require_test_database_url()
    os.environ["DB_SCHEMA"] = schema
    os.environ["USE_IN_MEMORY_REPOSITORY"] = "false"
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()


@pytest.fixture(scope="module")
def prepared_schemas() -> dict[str, str]:
    database_url = _require_test_database_url()
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")

    schemas = {
        "a": "test_user_a",
        "b": "test_user_b",
        "downgrade": "test_user_downgrade",
    }

    with engine.connect() as connection:
        for schema in schemas.values():
            connection.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))
            connection.execute(text(f"CREATE SCHEMA {schema}"))

    for schema in (schemas["a"], schemas["b"], schemas["downgrade"]):
        result = _run_alembic(schema, "upgrade", "head")
        assert result.returncode == 0, result.stderr or result.stdout

    yield schemas

    with engine.connect() as connection:
        for schema in schemas.values():
            connection.execute(text(f"DROP SCHEMA IF EXISTS {schema} CASCADE"))

    engine.dispose()


def test_alembic_upgrade_is_reentrant(prepared_schemas: dict[str, str]) -> None:
    for schema in (prepared_schemas["a"], prepared_schemas["b"]):
        result = _run_alembic(schema, "upgrade", "head")
        assert result.returncode == 0, result.stderr or result.stdout

    engine = create_engine(_require_test_database_url())
    with engine.connect() as connection:
        for schema in (prepared_schemas["a"], prepared_schemas["b"]):
            revision = connection.execute(text(f"SELECT version_num FROM {schema}.alembic_version")).scalar_one()
            assert revision == "20260715_0001"
    engine.dispose()


def test_postgres_crud_and_schema_isolation(prepared_schemas: dict[str, str], restore_env) -> None:
    _configure_runtime(prepared_schemas["a"])
    with TestClient(app) as client_a:
        members = client_a.get("/api/members")
        assert members.status_code == 200
        assert len(members.json()) == 3

        created = client_a.post(
            "/api/projects",
            json={
                "name": "SQL 전환 프로젝트",
                "owner_id": "member-kim",
                "owner_name": "김지훈",
                "description": "PostgreSQL CRUD 테스트",
                "start_date": "2026-07-15",
                "due_date": "2026-07-31",
                "priority": "HIGH",
                "invited_member_ids": ["member-lee", "member-park"],
            },
        )
        assert created.status_code == 201
        created_body = created.json()
        project_id = created_body["id"]
        assert created_body["invited_member_ids"] == ["member-lee", "member-park"]

        fetched = client_a.get(f"/api/projects/{project_id}")
        assert fetched.status_code == 200
        assert fetched.json()["name"] == "SQL 전환 프로젝트"

        listed = client_a.get("/api/projects")
        assert listed.status_code == 200
        assert [item["id"] for item in listed.json()][0] == project_id

        updated = client_a.put(
            f"/api/projects/{project_id}",
            json={
                "name": "SQL 전환 프로젝트 수정",
                "owner_id": "member-lee",
                "owner_name": "이수정",
                "description": None,
                "start_date": "2026-07-15",
                "due_date": "2026-08-05",
                "priority": "LOW",
                "invited_member_ids": ["member-park"],
            },
        )
        assert updated.status_code == 200
        assert updated.json()["owner_id"] == "member-lee"
        assert updated.json()["invited_member_ids"] == ["member-park"]

    _configure_runtime(prepared_schemas["b"])
    with TestClient(app) as client_b:
        missing = client_b.get(f"/api/projects/{project_id}")
        assert missing.status_code == 404
        empty = client_b.get("/api/projects")
        assert empty.status_code == 200
        assert empty.json() == []

    _configure_runtime(prepared_schemas["a"])
    with TestClient(app) as client_a:
        deleted = client_a.delete(f"/api/projects/{project_id}")
        assert deleted.status_code == 204
        assert client_a.get(f"/api/projects/{project_id}").status_code == 404


def test_firestore_repository_is_not_used_in_postgres_runtime(prepared_schemas: dict[str, str], restore_env) -> None:
    _configure_runtime(prepared_schemas["a"])
    with patch("app.features.projects.repository.firestore.Client", side_effect=AssertionError("firestore")):
        with TestClient(app) as client:
            response = client.get("/api/members")
            assert response.status_code == 200


def test_disposable_schema_downgrade(prepared_schemas: dict[str, str]) -> None:
    schema = prepared_schemas["downgrade"]
    result = _run_alembic(schema, "downgrade", "base")
    assert result.returncode == 0, result.stderr or result.stdout

    engine = create_engine(_require_test_database_url())
    inspector = inspect(engine)
    assert inspector.get_table_names(schema=schema) == ["alembic_version"]
    with engine.connect() as connection:
        remaining_revision = connection.execute(text(f"SELECT version_num FROM {schema}.alembic_version")).scalars().all()
    assert remaining_revision == []
    engine.dispose()


def test_public_schema_has_no_projectflow_tables(prepared_schemas: dict[str, str]) -> None:
    del prepared_schemas
    engine = create_engine(_require_test_database_url())
    with engine.connect() as connection:
        public_tables = connection.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name IN ('projects', 'project_invited_members', 'members', 'alembic_version')
                ORDER BY table_name
                """
            )
        ).scalars().all()
    assert public_tables == []
    engine.dispose()

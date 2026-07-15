from unittest.mock import patch

import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.core.database import build_database_url, create_database_engine


def _settings(**kwargs) -> Settings:
    return Settings(_env_file=None, **kwargs)


@patch("app.core.database.create_engine")
@patch("app.core.database.event.listens_for", side_effect=lambda target, identifier: (lambda fn: fn))
def test_postgresql_db_schema_sets_search_path(listens_for, create_engine) -> None:
    settings = _settings(
        app_env="test",
        database_url="postgresql://user:password@localhost/team_edu",
        db_schema="bkchoi21",
    )

    create_database_engine(settings)

    assert create_engine.call_args.kwargs["connect_args"] == {
        "options": "-csearch_path=bkchoi21",
    }
    assert create_engine.call_args.kwargs["pool_size"] == 1
    assert create_engine.call_args.kwargs["max_overflow"] == 0
    assert create_engine.call_args.kwargs["pool_timeout"] == 10
    assert create_engine.call_args.kwargs["pool_pre_ping"] is True
    assert create_engine.call_args.kwargs["pool_recycle"] == 1800
    assert create_engine.call_args.kwargs["pool_use_lifo"] is True


@patch("app.core.database.create_engine")
@patch("app.core.database.event.listens_for", side_effect=lambda target, identifier: (lambda fn: fn))
def test_db_schema_changes_selected_search_path(listens_for, create_engine) -> None:
    first = _settings(
        app_env="test",
        database_url="postgresql://user:password@localhost/team_edu",
        db_schema="bkchoi21",
    )
    second = _settings(
        app_env="test",
        database_url="postgresql://user:password@localhost/team_edu",
        db_schema="go23",
    )

    create_database_engine(first)
    create_database_engine(second)

    assert create_engine.call_args_list[0].kwargs["connect_args"]["options"] == "-csearch_path=bkchoi21"
    assert create_engine.call_args_list[1].kwargs["connect_args"]["options"] == "-csearch_path=go23"


def test_db_schema_rejects_sql_and_qualified_identifiers() -> None:
    with pytest.raises(ValidationError):
        _settings(app_env="test", database_url="postgresql://u:p@localhost/db", db_schema="public,bkchoi21")

    with pytest.raises(ValidationError):
        _settings(
            app_env="test",
            database_url="postgresql://u:p@localhost/db",
            db_schema="bkchoi21;drop schema public",
        )


def test_runtime_requires_db_schema_when_using_postgresql() -> None:
    with pytest.raises(ValidationError):
        _settings(
            app_env="education",
            use_in_memory_repository=False,
            database_url="postgresql://u:p@localhost/db",
            db_schema=None,
        )


def test_build_database_url_from_discrete_postgresql_fields() -> None:
    settings = _settings(
        app_env="test",
        db_schema="test_user_a",
        cloud_sql_host="127.0.0.1",
        cloud_sql_db="team_edu",
        cloud_sql_user="team_edu_master",
        cloud_sql_password="secret",
    )

    assert build_database_url(settings) == (
        "postgresql+psycopg2://team_edu_master:secret@127.0.0.1/team_edu"
    )


def test_pool_settings_can_be_overridden() -> None:
    settings = _settings(
        app_env="test",
        database_url="postgresql://u:p@localhost/db",
        db_schema="test_user_a",
        db_pool_size=2,
        db_max_overflow=3,
        db_pool_timeout=7,
        db_pool_recycle=600,
    )

    assert settings.db_pool_size == 2
    assert settings.db_max_overflow == 3
    assert settings.db_pool_timeout == 7
    assert settings.db_pool_recycle == 600


def test_pool_settings_reject_negative_values() -> None:
    with pytest.raises(ValidationError):
        _settings(
            app_env="test",
            database_url="postgresql://u:p@localhost/db",
            db_schema="test_user_a",
            db_pool_size=-1,
        )

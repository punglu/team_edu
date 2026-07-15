from __future__ import annotations

import os

import pytest

from app.core.config import get_settings
from app.core.database import get_engine, get_session_factory


@pytest.fixture(autouse=True)
def clear_runtime_caches() -> None:
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()
    yield
    get_settings.cache_clear()
    get_engine.cache_clear()
    get_session_factory.cache_clear()


@pytest.fixture
def restore_env() -> None:
    original = os.environ.copy()
    yield
    os.environ.clear()
    os.environ.update(original)

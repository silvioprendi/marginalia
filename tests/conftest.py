import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from marginalia.db import engine


def _postgres_is_up() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("select 1"))
    except OperationalError:
        return False
    return True


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Skip tests marked `db` when Postgres isn't running, instead of failing them."""
    if _postgres_is_up():
        return
    skip = pytest.mark.skip(reason="Postgres not running (docker compose up -d --wait)")
    for item in items:
        if "db" in item.keywords:
            item.add_marker(skip)

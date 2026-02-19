"""
Pytest fixtures for API tests.

Provides in-memory SQLite adapter and Redis mocking for isolated tests.
"""

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, patch

import pytest
from src.db.adapters.sqlite import SQLiteAdapter


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def sqlite_adapter() -> AsyncGenerator[SQLiteAdapter, None]:
    """In-memory SQLite adapter with a minimal schema for tests."""
    from sqlalchemy import text
    dsn = "sqlite+aiosqlite:///:memory:"
    adapter = SQLiteAdapter(dsn=dsn)
    await adapter.connect()
    async with adapter._engine.begin() as conn:
        await conn.execute(text(
            "CREATE TABLE test_users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)"
        ))
        await conn.execute(text(
            "INSERT INTO test_users (id, name) VALUES (1, 'alice'), (2, 'bob')"
        ))
    yield adapter
    await adapter.disconnect()


@pytest.fixture
def mock_redis_cache() -> Generator[None, None, None]:
    """Patch Redis cache so get_cached_result returns None (cache miss)."""
    with patch("src.agent.codeact_tool.get_cached_result", new_callable=AsyncMock) as get_mock, \
         patch("src.agent.codeact_tool.set_cached_result", new_callable=AsyncMock) as set_mock:
        get_mock.return_value = None
        yield

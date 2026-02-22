"""
Tests for DatabaseAdapter (SQLite in-memory): execute_query, get_tables, get_columns.
"""

import pytest
from src.db.adapters.sqlite import SQLiteAdapter


@pytest.mark.asyncio
async def test_execute_query_returns_columns_and_rows(sqlite_adapter) -> None:
    result = await sqlite_adapter.execute_query("SELECT id, name FROM test_users ORDER BY id")
    assert result["columns"] == ["id", "name"]
    assert result["row_count"] == 2
    assert len(result["rows"]) == 2
    assert result["rows"][0]["name"] == "alice"
    assert result["rows"][1]["name"] == "bob"


@pytest.mark.asyncio
async def test_execute_query_select_only(sqlite_adapter) -> None:
    with pytest.raises(ValueError, match="Potentially unsafe SQL detected"):
        await sqlite_adapter.execute_query("INSERT INTO test_users (id, name) VALUES (3, 'c')")
    with pytest.raises(ValueError, match="Potentially unsafe SQL detected"):
        await sqlite_adapter.execute_query("DELETE FROM test_users")


@pytest.mark.asyncio
async def test_get_tables(sqlite_adapter) -> None:
    tables = await sqlite_adapter.get_tables()
    assert "test_users" in tables


@pytest.mark.asyncio
async def test_get_columns(sqlite_adapter) -> None:
    cols = await sqlite_adapter.get_columns("test_users")
    names = [c["column"] for c in cols]
    assert "id" in names
    assert "name" in names
    assert all("type" in c and "nullable" in c for c in cols)


@pytest.mark.asyncio
async def test_ping(sqlite_adapter) -> None:
    assert await sqlite_adapter.ping() is True


@pytest.mark.asyncio
async def test_dialect(sqlite_adapter) -> None:
    assert sqlite_adapter.dialect == "sqlite"

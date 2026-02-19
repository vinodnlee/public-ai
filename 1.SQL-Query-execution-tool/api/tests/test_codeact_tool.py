"""
Tests for CodeActSQLTool: event stream, SQL extraction, cache, SELECT-only, errors.
"""

import pytest
from src.agent.codeact_tool import CodeActSQLTool
from src.agent.events import EventType
from src.semantic.layer import SemanticLayer


@pytest.mark.asyncio
async def test_extract_sql_plain(sqlite_adapter, mock_redis_cache) -> None:
    """Plain SQL without markdown fences is used as-is."""
    layer = SemanticLayer(sqlite_adapter)
    tool = CodeActSQLTool(sqlite_adapter, layer)
    sql = "SELECT id, name FROM test_users"
    events = []
    async for e in tool.run("list users", sql):
        events.append(e)
    assert any(e.type == EventType.SQL and e.content == sql for e in events)
    assert any(e.type == EventType.RESULT for e in events)
    result_ev = next(e for e in events if e.type == EventType.RESULT)
    assert result_ev.columns == ["id", "name"]
    assert result_ev.row_count == 2
    assert len(result_ev.rows or []) == 2


@pytest.mark.asyncio
async def test_extract_sql_from_markdown(sqlite_adapter, mock_redis_cache) -> None:
    """SQL inside ```sql fences is extracted."""
    layer = SemanticLayer(sqlite_adapter)
    tool = CodeActSQLTool(sqlite_adapter, layer)
    wrapped = "```sql\nSELECT name FROM test_users WHERE id = 1\n```"
    events = []
    async for e in tool.run("get one user", wrapped):
        events.append(e)
    sql_ev = next(e for e in events if e.type == EventType.SQL)
    assert "SELECT name FROM test_users" in (sql_ev.content or "")
    assert "```" not in (sql_ev.content or "")


@pytest.mark.asyncio
async def test_select_only_rejected(sqlite_adapter, mock_redis_cache) -> None:
    """Non-SELECT statements yield ERROR event."""
    layer = SemanticLayer(sqlite_adapter)
    tool = CodeActSQLTool(sqlite_adapter, layer)
    events = []
    async for e in tool.run("drop table", "INSERT INTO test_users (id, name) VALUES (3, 'x')"):
        events.append(e)
    assert any(e.type == EventType.ERROR for e in events)
    err_ev = next(e for e in events if e.type == EventType.ERROR)
    assert "SELECT" in (err_ev.content or "")


@pytest.mark.asyncio
async def test_tool_call_and_executing_events(sqlite_adapter, mock_redis_cache) -> None:
    """Stream includes TOOL_CALL, SQL, EXECUTING, RESULT."""
    layer = SemanticLayer(sqlite_adapter)
    tool = CodeActSQLTool(sqlite_adapter, layer)
    events = []
    async for e in tool.run("count users", "SELECT COUNT(*) AS n FROM test_users"):
        events.append(e)
    types = [e.type for e in events]
    assert EventType.TOOL_CALL in types
    assert EventType.SQL in types
    assert EventType.EXECUTING in types
    assert EventType.RESULT in types
    result_ev = next(e for e in events if e.type == EventType.RESULT)
    assert result_ev.row_count == 1
    assert (result_ev.rows or [{}])[0].get("n") == 2


@pytest.mark.asyncio
async def test_get_schema_context(sqlite_adapter) -> None:
    """get_schema_context returns a non-empty string with dialect and table info."""
    layer = SemanticLayer(sqlite_adapter)
    tool = CodeActSQLTool(sqlite_adapter, layer)
    ctx = await tool.get_schema_context()
    assert "sqlite" in ctx.lower()
    assert "test_users" in ctx or "schema" in ctx.lower()

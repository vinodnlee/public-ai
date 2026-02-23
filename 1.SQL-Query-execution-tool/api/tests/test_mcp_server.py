"""
Tests for MCP server: run_agent_and_collect and query_database tool.

Uses mocks so no real DB or LLM is required.
"""

import pytest

pytest.importorskip("fastmcp", reason="fastmcp not installed; skip MCP server tests")

from unittest.mock import AsyncMock, patch

from src.agent.events import AgentEvent, EventType
from src.mcp.run_agent import run_agent_and_collect


async def _fake_run(_query: str, _session_id: str):
    yield AgentEvent(type=EventType.PLAN, content="I will query the users table.")
    yield AgentEvent(type=EventType.ANSWER, content="There are 42 users.")
    yield AgentEvent(type=EventType.DONE)


@pytest.mark.asyncio
async def test_run_agent_and_collect_returns_answer() -> None:
    """When the agent yields ANSWER then DONE, the collected string is the answer."""
    with patch("src.mcp.run_agent.get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_get_adapter.return_value = mock_adapter
        with patch("src.mcp.run_agent.DeepAgent") as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.run = _fake_run
            mock_agent_class.return_value = mock_agent

            result = await run_agent_and_collect("How many users?")

    assert result == "There are 42 users."


@pytest.mark.asyncio
async def test_run_agent_and_collect_includes_result_summary() -> None:
    """When the agent yields RESULT with row_count, it is appended to the answer."""
    async def _fake_run_with_result(_query: str, _session_id: str):
        yield AgentEvent(type=EventType.RESULT, row_count=10)
        yield AgentEvent(type=EventType.ANSWER, content="Done.")
        yield AgentEvent(type=EventType.DONE)

    with patch("src.mcp.run_agent.get_adapter", return_value=AsyncMock()), \
         patch("src.mcp.run_agent.DeepAgent") as mock_agent_class:
        mock_agent_class.return_value = AsyncMock(run=_fake_run_with_result)
        result = await run_agent_and_collect("Count rows")

    assert "Done." in result
    assert "(Query returned 10 rows.)" in result


@pytest.mark.asyncio
async def test_run_agent_and_collect_interrupt_returns_approval_message() -> None:
    """When the agent yields INTERRUPT, return message directing to web UI."""
    async def _fake_run_interrupt(_query: str, _session_id: str):
        yield AgentEvent(type=EventType.INTERRUPT, proposed_sql="DELETE FROM t")

    with patch("src.mcp.run_agent.get_adapter", return_value=AsyncMock()), \
         patch("src.mcp.run_agent.DeepAgent") as mock_agent_class:
        mock_agent_class.return_value = AsyncMock(run=_fake_run_interrupt)
        result = await run_agent_and_collect("Delete everything")

    assert "approval" in result.lower()
    assert "web UI" in result

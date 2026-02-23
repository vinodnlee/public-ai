"""
Tests for MCP tool conversion: MCP tool schemas to LangChain BaseTool.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.mcp.tools import mcp_tools_to_langchain


def test_mcp_tools_to_langchain_empty_list_returns_empty() -> None:
    """When tools list is empty, return empty list."""
    async def noop_call(_name: str, _args: dict):
        return []
    result = mcp_tools_to_langchain([], noop_call)
    assert result == []


def test_mcp_tools_to_langchain_converts_schema_to_tool_with_name_and_description() -> None:
    """One MCP tool schema becomes a LangChain tool with correct name and description."""
    tools = [
        {
            "name": "get_weather",
            "description": "Get the current weather",
            "inputSchema": {
                "type": "object",
                "properties": {"location": {"type": "string"}},
                "required": ["location"],
            },
        }
    ]
    call_log: list[tuple[str, dict]] = []

    async def record_call(name: str, arguments: dict):
        call_log.append((name, arguments))
        return {"content": [{"type": "text", "text": "sunny"}]}

    result = mcp_tools_to_langchain(tools, record_call)
    assert len(result) == 1
    assert result[0].name == "get_weather"
    assert "weather" in (result[0].description or "").lower()


@pytest.mark.asyncio
async def test_mcp_tools_to_langchain_invoke_calls_call_tool_with_name_and_args() -> None:
    """Invoking the generated tool calls the provided call_tool with name and parsed args."""
    tools = [
        {
            "name": "echo",
            "description": "Echo back the input",
            "inputSchema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
            },
        }
    ]
    call_log: list[tuple[str, dict]] = []

    async def record_call(name: str, arguments: dict):
        call_log.append((name, arguments))
        return {"content": [{"type": "text", "text": "ok"}]}

    result = mcp_tools_to_langchain(tools, record_call)
    assert len(result) == 1
    tool = result[0]
    # LangChain tools are sync by default; we need to support async invoke
    if hasattr(tool, "ainvoke"):
        await tool.ainvoke({"message": "hello"})
    else:
        tool.invoke({"message": "hello"})
    assert len(call_log) == 1
    assert call_log[0][0] == "echo"
    assert call_log[0][1].get("message") == "hello"

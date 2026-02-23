"""
Tests for MCP client loader used by deepagent_builder.
"""

import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from src.mcp.client import (
    get_mcp_tools_for_supervisor,
    _expand_mcp_server_entries,
    _normalize_mcp_arguments,
    _make_call_tool,
)


def test_get_mcp_tools_for_supervisor_empty_servers_returns_empty() -> None:
    settings = SimpleNamespace(mcp_servers=[])
    assert get_mcp_tools_for_supervisor(settings) == []


def test_get_mcp_tools_for_supervisor_loads_tools_from_server() -> None:
    settings = SimpleNamespace(mcp_servers=["http://mcp.local"])
    fake_tool = SimpleNamespace(name="weather", description="weather")

    with patch("src.mcp.client._MCP_TOOLS_CACHE", {}), \
         patch("src.mcp.client._load_mcp_tools_for_server", return_value=[{"name": "weather", "description": "", "inputSchema": {}}]), \
         patch("src.mcp.client.mcp_tools_to_langchain", return_value=[fake_tool]):
        tools = get_mcp_tools_for_supervisor(settings)
        assert len(tools) == 1
        assert tools[0].name == "weather"


def test_get_mcp_tools_for_supervisor_skips_duplicate_names() -> None:
    settings = SimpleNamespace(mcp_servers=["s1", "s2"])
    tool1 = SimpleNamespace(name="echo", description="a")
    tool2 = SimpleNamespace(name="echo", description="b")

    with patch("src.mcp.client._MCP_TOOLS_CACHE", {}), \
         patch("src.mcp.client._load_mcp_tools_for_server", side_effect=[
             [{"name": "echo", "description": "", "inputSchema": {}}],
             [{"name": "echo", "description": "", "inputSchema": {}}],
         ]), \
         patch("src.mcp.client.mcp_tools_to_langchain", side_effect=[[tool1], [tool2]]):
        tools = get_mcp_tools_for_supervisor(settings)
        assert len(tools) == 1
        assert tools[0].name == "echo"


def test_expand_mcp_server_entries_supports_standard_mcpservers_json() -> None:
    raw = json.dumps(
        {
            "mcpServers": {
                "chrome-devtools": {
                    "command": "npx",
                    "args": ["-y", "chrome-devtools-mcp@latest"],
                }
            }
        }
    )
    expanded = _expand_mcp_server_entries([raw])
    assert len(expanded) == 1
    label, transport = expanded[0]
    assert label == "chrome-devtools"
    assert isinstance(transport, dict)
    assert "mcpServers" in transport
    assert transport["mcpServers"]["chrome-devtools"]["command"] == "npx"


def test_get_mcp_tools_for_supervisor_accepts_standard_mcpservers_json() -> None:
    settings = SimpleNamespace(
        mcp_servers=[
            json.dumps(
                {
                    "mcpServers": {
                        "chrome-devtools": {
                            "command": "npx",
                            "args": ["-y", "chrome-devtools-mcp@latest"],
                        }
                    }
                }
            )
        ]
    )
    fake_tool = SimpleNamespace(name="browser_navigate", description="browser")

    with patch("src.mcp.client._MCP_TOOLS_CACHE", {}), \
         patch("src.mcp.client._load_mcp_tools_for_server", return_value=[{"name": "browser_navigate", "description": "", "inputSchema": {}}]) as m_load, \
         patch("src.mcp.client.mcp_tools_to_langchain", return_value=[fake_tool]):
        tools = get_mcp_tools_for_supervisor(settings)
        assert len(tools) == 1
        assert tools[0].name == "browser_navigate"
        call_transport = m_load.call_args[0][0]
        assert isinstance(call_transport, dict)
        assert "mcpServers" in call_transport
        assert call_transport["mcpServers"]["chrome-devtools"]["command"] == "npx"


def test_normalize_mcp_arguments_sets_default_url_for_new_page() -> None:
    assert _normalize_mcp_arguments("new_page", {})["url"] == "about:blank"
    assert _normalize_mcp_arguments("new_page", {"url": "https://example.com"})["url"] == "https://example.com"
    assert _normalize_mcp_arguments("goto", {}) == {}


@pytest.mark.asyncio
async def test_make_call_tool_reuses_same_client_for_same_server() -> None:
    server = {"mcpServers": {"chrome-devtools": {"command": "npx", "args": ["-y", "chrome-devtools-mcp@latest", "--isolated"]}}}
    call_tool = _make_call_tool(server)

    class FakeClient:
        entered = 0
        called = 0

        async def __aenter__(self):
            FakeClient.entered += 1
            return self

        async def call_tool(self, _name, arguments):
            FakeClient.called += 1
            return {"content": [{"type": "text", "text": str(arguments)}]}

    with patch("src.mcp.client._MCP_CLIENTS", {}), \
         patch("src.mcp.client._MCP_CLIENT_INIT_LOCKS", {}), \
         patch("src.mcp.client._MCP_CLIENT_CALL_LOCKS", {}), \
         patch("fastmcp.Client", return_value=FakeClient()):
        await call_tool("list_pages", {})
        await call_tool("navigate_page", {"url": "https://www.baidu.com"})
        assert FakeClient.entered == 1
        assert FakeClient.called == 2

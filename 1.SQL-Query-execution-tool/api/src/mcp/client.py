"""
MCP client: load tools from configured MCP servers for the supervisor agent.

When mcp_servers is non-empty, attempts to connect and convert tools to LangChain format.
Returns an empty list when no servers are configured or on connection/parse errors.
"""

from typing import Any

from src.log import get_logger

logger = get_logger(__name__)


def get_mcp_tools_for_supervisor(settings: Any) -> list[Any]:
    """
    Return a list of LangChain tools from configured MCP servers.

    Uses settings.mcp_servers (list of server URLs or "stdio:command:args" specs).
    Returns [] when mcp_servers is empty or when no tools could be loaded.
    """
    servers = getattr(settings, "mcp_servers", None) or []
    if not servers:
        return []

    # TODO: connect to each server (e.g. via MCP Python SDK), list_tools, convert
    # with mcp_tools_to_langchain and a call_tool that invokes the server.
    # For now we return [] so the builder can merge this list without error.
    logger.debug("MCP servers configured but client not yet implemented: %s", servers)
    return []

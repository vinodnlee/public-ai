"""
MCP client: load tools from configured MCP servers for the supervisor agent.
"""

from __future__ import annotations

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from src.log import get_logger
from src.mcp.tools import mcp_tools_to_langchain

logger = get_logger(__name__)

_MCP_TOOLS_CACHE: dict[tuple[str, ...], list[Any]] = {}


def _tool_to_schema(tool: Any) -> dict[str, Any]:
    """Normalize a fastmcp/mcp Tool object to schema dict."""
    if hasattr(tool, "model_dump"):
        raw = tool.model_dump()
    elif isinstance(tool, dict):
        raw = tool
    else:
        raw = {
            "name": getattr(tool, "name", "unnamed"),
            "description": getattr(tool, "description", ""),
            "inputSchema": getattr(tool, "inputSchema", None),
        }

    return {
        "name": raw.get("name") or "unnamed",
        "description": raw.get("description") or "",
        "inputSchema": raw.get("inputSchema") or raw.get("input_schema") or {},
    }


def _run_coro_sync(coro: Any) -> Any:
    """Run async code from sync context, even if an event loop is active."""
    try:
        asyncio.get_running_loop()
        in_running_loop = True
    except RuntimeError:
        in_running_loop = False

    if not in_running_loop:
        return asyncio.run(coro)

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(asyncio.run, coro)
        return future.result()


def _transport_cache_key(transport: Any) -> str:
    if isinstance(transport, str):
        return transport
    try:
        return json.dumps(transport, sort_keys=True, ensure_ascii=True)
    except Exception:
        return str(transport)


def _expand_mcp_server_entries(entries: list[Any]) -> list[tuple[str, Any]]:
    """Expand mcp server entries into (label, transport) tuples.

    Supports:
    - URL string entries
    - Single transport JSON object string
    - Standard config object string: {"mcpServers": {"name": {...}}}
    """
    expanded: list[tuple[str, Any]] = []
    for raw in entries:
        value: Any = raw
        if isinstance(raw, str):
            text = raw.strip()
            if not text:
                continue
            if text.startswith("{"):
                try:
                    value = json.loads(text)
                except Exception:
                    value = text
            else:
                value = text

        if isinstance(value, dict) and isinstance(value.get("mcpServers"), dict):
            for name, transport in value["mcpServers"].items():
                if transport is None:
                    continue
                expanded.append((str(name), {"mcpServers": {str(name): transport}}))
            continue

        if isinstance(value, dict):
            expanded.append(("inline", {"mcpServers": {"inline": value}}))
            continue

        expanded.append((str(value), value))

    return expanded


def _load_mcp_tools_for_server(server: Any) -> list[dict[str, Any]]:
    """List tool schemas from one MCP server; return [] on failure."""
    async def _list_tools() -> list[dict[str, Any]]:
        from fastmcp import Client

        async with Client(server) as client:
            tools = await client.list_tools()
            return [_tool_to_schema(t) for t in tools]

    try:
        return _run_coro_sync(_list_tools())
    except Exception as exc:
        logger.warning("Failed loading MCP tools from server '%s': %s", server, exc)
        return []


def _normalize_mcp_arguments(name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize tool arguments before dispatching to MCP server."""
    args = dict(arguments or {})
    if name == "new_page" and not args.get("url"):
        # chrome-devtools-mcp requires url for new_page.
        args["url"] = "about:blank"
    return args


def _make_call_tool(server: Any):
    """Create async callback used by LangChain StructuredTools."""
    async def _call_tool(name: str, arguments: dict[str, Any]) -> Any:
        from fastmcp import Client

        normalized_args = _normalize_mcp_arguments(name, arguments)
        async with Client(server) as client:
            result = await client.call_tool(name, arguments=normalized_args)
            if hasattr(result, "model_dump"):
                return result.model_dump()
            return result

    return _call_tool


def get_mcp_tools_for_supervisor(settings: Any) -> list[Any]:
    """Return LangChain tools from all configured MCP servers.

    Uses settings.mcp_servers (URLs or stdio specs). Errors are logged and skipped.
    """
    raw_servers = list(getattr(settings, "mcp_servers", None) or [])
    expanded_servers = _expand_mcp_server_entries(raw_servers)
    if not expanded_servers:
        return []

    cache_key = tuple(_transport_cache_key(transport) for _, transport in expanded_servers)
    if cache_key in _MCP_TOOLS_CACHE:
        return _MCP_TOOLS_CACHE[cache_key]

    all_tools: list[Any] = []
    seen_names: set[str] = set()
    for label, server in expanded_servers:
        schemas = _load_mcp_tools_for_server(server)
        if not schemas:
            continue

        converted = mcp_tools_to_langchain(schemas, _make_call_tool(server))
        for tool in converted:
            name = getattr(tool, "name", "")
            if name and name in seen_names:
                logger.warning(
                    "Duplicate MCP tool name '%s' from server '%s'; skipping duplicate.",
                    name,
                    label,
                )
                continue
            seen_names.add(name)
            all_tools.append(tool)

    _MCP_TOOLS_CACHE[cache_key] = all_tools
    logger.info("Loaded %d MCP tools from %d servers", len(all_tools), len(expanded_servers))
    return all_tools

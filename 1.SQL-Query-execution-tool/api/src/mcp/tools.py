"""
Convert MCP tool definitions to LangChain BaseTool.

Accepts a list of MCP tool schemas (name, description, inputSchema) and an async call_tool
callback; returns a list of LangChain tools that invoke the callback when run.
"""

from typing import Any, Callable

from langchain_core.tools import StructuredTool

# JSON schema that accepts any object so input dict is passed through as kwargs.
_ANY_OBJECT_SCHEMA = {"type": "object", "properties": {}, "additionalProperties": True}


def mcp_tools_to_langchain(
    tools: list[dict[str, Any]],
    call_tool: Callable[[str, dict[str, Any]], Any],
) -> list[StructuredTool]:
    """
    Convert MCP tool schemas to LangChain StructuredTools.

    Each tool, when invoked, calls call_tool(tool_name, arguments).
    call_tool should be async and return the MCP call_tool result (e.g. content list).
    """
    result: list[StructuredTool] = []

    def _make_invoke(tool_name: str):
        async def _invoke(**kwargs: Any) -> str:
            out = await call_tool(tool_name, kwargs)
            if isinstance(out, dict) and "content" in out:
                texts = [
                    c.get("text", "")
                    for c in out["content"]
                    if isinstance(c, dict) and c.get("type") == "text"
                ]
                return "\n".join(texts)
            return str(out)
        return _invoke

    for t in tools:
        name = t.get("name") or "unnamed"
        description = t.get("description") or ""

        tool = StructuredTool.from_function(
            coroutine=_make_invoke(name),
            name=name,
            description=description,
            args_schema=_ANY_OBJECT_SCHEMA,
        )
        result.append(tool)
    return result

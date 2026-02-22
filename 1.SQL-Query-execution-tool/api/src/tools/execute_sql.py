"""Execute SQL tool — runs a read-only SELECT and returns JSON results."""

import json
import re
from typing import Any

from langchain_core.tools import InjectedToolArg, tool
from typing_extensions import Annotated

from src.log import get_logger
from src.agent.events import AgentEvent, EventType
from src.cache.redis_client import get_cached_result, set_cached_result
from src.db.adapters.base import DatabaseAdapter

logger = get_logger(__name__)


def _extract_sql(text: str) -> str:
    match = re.search(r"```(?:sql)?\s*([\s\S]+?)```", text, re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()


@tool(parse_docstring=True)
async def execute_sql(
    nl_query: str,
    sql: str,
    adapter: Annotated[DatabaseAdapter, InjectedToolArg],
    captured_events: Annotated[list, InjectedToolArg],
) -> str:
    """Execute a read-only SELECT query and return results as JSON.

    Args:
        nl_query: The original natural language question from the user.
        sql: The SELECT SQL statement to execute.
        adapter: The database adapter instance (injected at runtime).
        captured_events: Shared list to capture AgentEvents for re-emission (injected at runtime).

    Returns:
        JSON string with keys: sql, columns, rows, row_count, error.
    """
    captured_events.clear()
    clean_sql = _extract_sql(sql)
    logger.info("execute_sql | dialect=%s sql=%s", adapter.dialect, clean_sql[:120])

    result_payload: dict[str, Any] = {
        "sql": clean_sql,
        "columns": [],
        "rows": [],
        "row_count": 0,
        "error": None,
    }

    captured_events.append(
        AgentEvent(type=EventType.TOOL_CALL, tool="codeact_sql", input=nl_query)
    )
    captured_events.append(
        AgentEvent(type=EventType.SQL, content=clean_sql)
    )

    cached = await get_cached_result(clean_sql)
    if cached:
        logger.info("Cache hit for SQL query")
        captured_events.append(
            AgentEvent(type=EventType.EXECUTING, content="Returning cached result...")
        )
        captured_events.append(
            AgentEvent(
                type=EventType.RESULT,
                columns=cached["columns"],
                rows=cached["rows"],
                row_count=cached["row_count"],
            )
        )
        result_payload.update(
            columns=cached["columns"],
            rows=cached["rows"],
            row_count=cached["row_count"],
        )
        return json.dumps(result_payload)

    captured_events.append(
        AgentEvent(
            type=EventType.EXECUTING,
            content=f"Running query on {adapter.dialect}...",
        )
    )

    try:
        result: dict[str, Any] = await adapter.execute_query(clean_sql)
        await set_cached_result(clean_sql, result)
        logger.info("Query returned %d rows", result["row_count"])
        captured_events.append(
            AgentEvent(
                type=EventType.RESULT,
                columns=result["columns"],
                rows=result["rows"],
                row_count=result["row_count"],
            )
        )
        result_payload.update(
            columns=result["columns"],
            rows=result["rows"],
            row_count=result["row_count"],
        )
    except Exception as exc:
        logger.error("Query execution failed: %s", exc)
        captured_events.append(
            AgentEvent(type=EventType.ERROR, content=str(exc))
        )
        result_payload["error"] = str(exc)

    return json.dumps(result_payload)

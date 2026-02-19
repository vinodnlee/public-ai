"""
CodeAct SQL Tool.

Receives a natural language query + the LLM-generated SQL,
executes it via the database adapter, and yields a stream of
AgentEvent objects for real-time SSE delivery to the UI.
"""

import re
from typing import AsyncGenerator, Any
from src.agent.events import AgentEvent, EventType
from src.cache.redis_client import get_cached_result, set_cached_result
from src.db.adapters.base import DatabaseAdapter
from src.semantic.layer import SemanticLayer


class CodeActSQLTool:
    """
    CodeAct Agent Tool — generates and executes SQL queries.

    Works against any DatabaseAdapter implementation; has no direct
    knowledge of PostgreSQL, MySQL, or SQLite.
    """

    TOOL_NAME = "codeact_sql"

    def __init__(self, adapter: DatabaseAdapter, semantic_layer: SemanticLayer) -> None:
        self._adapter = adapter
        self._semantic_layer = semantic_layer

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(
        self, natural_language_query: str, generated_sql: str
    ) -> AsyncGenerator[AgentEvent, None]:
        """Yield AgentEvent stream for a given NL query + LLM-generated SQL."""

        yield AgentEvent(
            type=EventType.TOOL_CALL,
            tool=self.TOOL_NAME,
            input=natural_language_query,
        )

        sql = self._extract_sql(generated_sql)
        yield AgentEvent(type=EventType.SQL, content=sql)

        # Cache hit
        cached = await get_cached_result(sql)
        if cached:
            yield AgentEvent(type=EventType.EXECUTING, content="Returning cached result...")
            yield AgentEvent(
                type=EventType.RESULT,
                columns=cached["columns"],
                rows=cached["rows"],
                row_count=cached["row_count"],
            )
            return

        yield AgentEvent(
            type=EventType.EXECUTING,
            content=f"Running query on {self._adapter.dialect}...",
        )

        try:
            result: dict[str, Any] = await self._adapter.execute_query(sql)
            await set_cached_result(sql, result)
            yield AgentEvent(
                type=EventType.RESULT,
                columns=result["columns"],
                rows=result["rows"],
                row_count=result["row_count"],
            )
        except Exception as exc:
            yield AgentEvent(type=EventType.ERROR, content=str(exc))

    async def get_schema_context(self) -> str:
        """
        Return the full semantic + physical schema context string
        for injection into the LLM system prompt.
        """
        return await self._semantic_layer.build_prompt_context()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_sql(text: str) -> str:
        """Strip SQL from markdown code fences if present."""
        match = re.search(r"```(?:sql)?\s*([\s\S]+?)```", text, re.IGNORECASE)
        return match.group(1).strip() if match else text.strip()

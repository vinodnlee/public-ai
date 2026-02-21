"""
DeepAgent orchestrator — deepagents package implementation.

Builds a supervisor + sql-executor subagent graph using
`deepagents.create_deep_agent`. The CodeAct SQL tool is registered
as a LangChain tool and handed to the sql-executor subagent.

Streams fine-grained AgentEvents via LangGraph astream_events(v2),
translated into the SSE event types consumed by the FastAPI endpoint.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, AsyncGenerator

from deepagents import create_deep_agent  # type: ignore
from langchain_core.tools import tool as lc_tool
from langchain_openai import ChatOpenAI  # type: ignore
from langgraph.checkpoint.memory import InMemorySaver  # type: ignore

from src.agent.codeact_tool import CodeActSQLTool
from src.agent.events import AgentEvent, EventType
from src.cache.redis_client import get_session_history, set_session_history
from src.config.settings import get_settings
from src.db.adapters.base import DatabaseAdapter
from src.semantic.layer import SemanticLayer

settings = get_settings()

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

SUPERVISOR_PROMPT_TEMPLATE = """\
You are a SQL data analyst supervisor coordinating a sql-executor subagent.

Your responsibilities:
1. Receive the user’s natural language question.
2. Delegate it to the ‘sql-executor’ subagent with the full user question.
3. Summarise the subagent’s results in clear, plain English.

Database dialect : {dialect}

Schema context:
{schema_context}

NEVER generate or allow INSERT, UPDATE, DELETE, DROP, TRUNCATE, or ALTER.
"""

SQL_EXECUTOR_PROMPT = """\
You are a SQL execution specialist.

Given a natural language question:
1. Generate a safe, read-only SELECT statement.
2. Call the `execute_sql` tool with:
   - `nl_query`: the original question
   - `sql`     : your SELECT statement
3. Return the JSON result from the tool plus a brief explanation.

SELECT queries only — never DDL or DML.
"""


# ---------------------------------------------------------------------------
# DeepAgent
# ---------------------------------------------------------------------------

class DeepAgent:
    """
    Supervisor + subagent orchestrator built on `deepagents.create_deep_agent`.

    Architecture
    ────────────
    Supervisor
      └─ sql-executor subagent
           └─ execute_sql tool  →  CodeActSQLTool  →  DatabaseAdapter

    The graph uses InMemorySaver as its checkpointer so conversation
    history is maintained across turns within the same DeepAgent instance.
    Each public `run()` call maps to a Redis session_id → LangGraph thread_id.
    """

    def __init__(self, adapter: DatabaseAdapter) -> None:
        self._adapter = adapter
        self._semantic_layer = SemanticLayer(adapter)
        self._codeact = CodeActSQLTool(adapter, self._semantic_layer)
        self._checkpointer = InMemorySaver()
        self._captured_events: list[AgentEvent] = []
        # thread_id cache: redis session_id → langgraph thread_id
        self._thread_map: dict[str, str] = {}

    # ------------------------------------------------------------------
    # LangChain tool
    # ------------------------------------------------------------------

    def _make_execute_sql_tool(self):
        """
        Return a LangChain @tool that wraps CodeActSQLTool.run().

        All intermediate AgentEvents (SQL, EXECUTING, RESULT, ERROR) are
        captured in self._captured_events so they can be re-emitted inside
        the main streaming loop at `on_tool_end`.
        """
        agent_self = self  # closure

        @lc_tool
        async def execute_sql(nl_query: str, sql: str) -> str:  # noqa: WPS430
            """Execute a read-only SELECT query and return results as JSON.

            Args:
                nl_query: The original natural language question.
                sql: The SELECT SQL statement to execute.
            """
            agent_self._captured_events.clear()
            result_payload: dict[str, Any] = {
                "sql": sql,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "error": None,
            }
            async for event in agent_self._codeact.run(nl_query, sql):
                agent_self._captured_events.append(event)
                if event.type == EventType.RESULT:
                    result_payload.update(
                        columns=event.columns or [],
                        rows=event.rows or [],
                        row_count=event.row_count or 0,
                    )
                elif event.type == EventType.ERROR:
                    result_payload["error"] = event.content
            return json.dumps(result_payload)

        return execute_sql

    # ------------------------------------------------------------------
    # Agent graph builder
    # ------------------------------------------------------------------

    async def _build_graph(self, schema_context: str):
        """Build (or rebuild) the deepagents supervisor graph."""
        model_kwargs: dict[str, Any] = {
            "model": settings.llm_model,
            "api_key": settings.llm_api_key,
            "max_tokens": settings.llm_max_tokens,
            "temperature": settings.llm_temperature,
        }
        if settings.llm_base_url:
            model_kwargs["base_url"] = settings.llm_base_url.rstrip("/")
        model = ChatOpenAI(**model_kwargs)

        sql_tool = self._make_execute_sql_tool()

        subagents = [
            {
                "name": "sql-executor",
                "description": (
                    "Generates and executes safe SELECT SQL queries against the "
                    "database and returns structured results."
                ),
                "system_prompt": SQL_EXECUTOR_PROMPT,
                "tools": [sql_tool],
            }
        ]

        supervisor_prompt = SUPERVISOR_PROMPT_TEMPLATE.format(
            dialect=self._adapter.dialect,
            schema_context=schema_context,
        )

        graph = create_deep_agent(
            model=model,
            tools=[],                   # supervisor has no direct tools
            system_prompt=supervisor_prompt,
            subagents=subagents,
            checkpointer=self._checkpointer,
        )
        return graph

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def run(
        self, query: str, session_id: str
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        Run the deepagents supervisor pipeline and yield AgentEvents.

        Flow:
          1. Load Redis history to restore conversation context
          2. Build semantic schema context
          3. Build deepagents supervisor graph
          4. Stream via graph.astream_events(version="v2")
             • on_chat_model_stream → TOKEN
             • on_tool_start        → TOOL_CALL + SQL + THINKING
             • on_tool_end          → re-emit captured RESULT/ERROR events
          5. Persist updated history to Redis
        """
        # Map session_id → stable LangGraph thread_id
        if session_id not in self._thread_map:
            self._thread_map[session_id] = uuid.uuid4().hex
        thread_id = self._thread_map[session_id]

        yield AgentEvent(type=EventType.THINKING, content="Analyzing your question...")

        try:
            schema_context = await self._codeact.get_schema_context()
        except OSError as e:
            yield AgentEvent(
                type=EventType.ERROR,
                content=(
                    "Database connection failed. Please ensure PostgreSQL is running "
                    "(e.g. start with: docker compose -f deploy/docker-compose.local.yml up -d). "
                    f"Detail: {e!s}"
                ),
            )
            yield AgentEvent(type=EventType.DONE)
            return
        except Exception as e:
            yield AgentEvent(
                type=EventType.ERROR,
                content=f"Failed to load schema: {e!s}",
            )
            yield AgentEvent(type=EventType.DONE)
            return

        graph = await self._build_graph(schema_context)

        yield AgentEvent(type=EventType.THINKING, content="Generating SQL query...")

        # Load conversation history from Redis so the model has context across turns
        history = await get_session_history(session_id) or []
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in history
            if isinstance(m.get("role"), str) and isinstance(m.get("content"), str)
        ]
        messages.append({"role": "user", "content": query})

        config = {"configurable": {"thread_id": thread_id}}
        input_payload = {"messages": messages}

        full_response_parts: list[str] = []

        # ── Stream deepagents graph events ─────────────────────────────
        async for lc_event in graph.astream_events(
            input_payload, config=config, version="v2"
        ):
            kind: str = lc_event["event"]

            # LLM token streaming (supervisor + subagent)
            if kind == "on_chat_model_stream":
                chunk = lc_event["data"].get("chunk")
                if chunk and chunk.content:
                    full_response_parts.append(chunk.content)
                    yield AgentEvent(type=EventType.TOKEN, content=chunk.content)

            # Tool call started — emit TOOL_CALL + SQL + THINKING
            elif kind == "on_tool_start":
                tool_input: dict = lc_event.get("data", {}).get("input", {})
                yield AgentEvent(
                    type=EventType.TOOL_CALL,
                    tool="sql_executor",
                    input=tool_input.get("nl_query", query),
                )
                if sql_text := tool_input.get("sql"):
                    yield AgentEvent(type=EventType.SQL, content=sql_text)
                yield AgentEvent(
                    type=EventType.THINKING, content="Executing SQL on database..."
                )

            # Tool call finished — re-emit all captured CodeAct events
            elif kind == "on_tool_end":
                for captured in self._captured_events:
                    yield captured

        # ── Persist conversation turn to Redis ───────────────────────────
        full_response = "".join(full_response_parts)
        new_history = messages + \
            [{"role": "assistant", "content": full_response}]
        # keep last 10 turns (20 messages)
        await set_session_history(session_id, new_history[-20:])

        yield AgentEvent(type=EventType.DONE)

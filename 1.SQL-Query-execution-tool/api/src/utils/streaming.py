"""Streaming utilities for parsing and yielding agent events."""

from typing import AsyncIterator, AsyncGenerator
from src.agent.events import AgentEvent, EventType
from src.log import get_logger

logger = get_logger(__name__)


async def stream_agent_events(
    graph_stream: AsyncIterator[dict],
    original_query: str,
    captured_events: list[AgentEvent],
    full_response_parts: list[str],
) -> AsyncGenerator[AgentEvent, None]:
    """
    Consume LangGraph stream events and yield unified AgentEvents.
    Mutates `full_response_parts` to capture the final assistant message.
    """
    async for lc_event in graph_stream:
        kind: str = lc_event.get("event", "")

        if kind == "on_chat_model_stream":
            chunk = lc_event.get("data", {}).get("chunk")
            if chunk and chunk.content:
                full_response_parts.append(chunk.content)
                yield AgentEvent(type=EventType.TOKEN, content=chunk.content)

        elif kind == "on_tool_start":
            tool_input: dict = lc_event.get("data", {}).get("input", {})
            logger.info("Tool call started | input=%s", tool_input)
            yield AgentEvent(
                type=EventType.TOOL_CALL,
                tool="sql_executor",
                input=tool_input.get("nl_query", original_query),
            )
            if sql_text := tool_input.get("sql"):
                yield AgentEvent(type=EventType.SQL, content=sql_text)
            yield AgentEvent(
                type=EventType.THINKING, content="Executing SQL on database..."
            )

        elif kind == "on_tool_end":
            for captured in captured_events:
                yield captured

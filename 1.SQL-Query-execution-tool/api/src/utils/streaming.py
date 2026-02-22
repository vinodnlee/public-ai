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

    * Buffers LLM tokens and emits them as a single PLAN event (before the
      first tool call) or a single ANSWER event (after the last tool result).
    * Tool execution details (TOOL_CALL, SQL, EXECUTING, RESULT, ERROR) come
      exclusively from `captured_events` populated by execute_sql, avoiding
      the duplicate events that `on_tool_start` used to produce.
    * Mutates `full_response_parts` so the caller can persist the response.
    """
    token_buffer: list[str] = []
    plan_emitted = False

    async for lc_event in graph_stream:
        kind: str = lc_event.get("event", "")

        if kind == "on_chat_model_stream":
            chunk = lc_event.get("data", {}).get("chunk")
            if chunk and chunk.content:
                token_buffer.append(chunk.content)
                full_response_parts.append(chunk.content)

        elif kind == "on_tool_start":
            # Flush buffered tokens as PLAN (once) before any tool runs
            if token_buffer and not plan_emitted:
                plan_text = "".join(token_buffer).strip()
                if plan_text:
                    yield AgentEvent(type=EventType.PLAN, content=plan_text)
                    plan_emitted = True
                token_buffer.clear()
            elif token_buffer:
                # Intermediate reasoning between tool calls — discard
                token_buffer.clear()

            tool_name = lc_event.get("name", "")
            logger.info("Tool call started | tool=%s", tool_name)

        elif kind == "on_tool_end":
            for captured in captured_events:
                yield captured
            captured_events.clear()

    # Flush remaining tokens as the final ANSWER
    if token_buffer:
        answer_text = "".join(token_buffer).strip()
        if answer_text:
            yield AgentEvent(type=EventType.ANSWER, content=answer_text)
        token_buffer.clear()

"""Streaming utilities for parsing and yielding agent events."""

from typing import Any, AsyncIterator, AsyncGenerator
from src.agent.events import AgentEvent, EventType
from src.log import get_logger

logger = get_logger(__name__)


def _extract_interrupt_payload(lc_event: dict) -> dict[str, Any] | None:
    """Return HITLRequest dict if this event carries __interrupt__, else None."""
    data = lc_event.get("data") or {}
    interrupt = data.get("__interrupt__")
    if interrupt is not None:
        return interrupt if isinstance(interrupt, dict) else None
    output = data.get("output")
    if isinstance(output, dict) and "__interrupt__" in output:
        val = output["__interrupt__"]
        return val if isinstance(val, dict) else None
    return None


def _interrupt_to_agent_event(hitl_request: dict[str, Any]) -> AgentEvent | None:
    """Build an INTERRUPT AgentEvent from a HITLRequest (action_requests with execute_sql_query)."""
    action_requests = hitl_request.get("action_requests") or []
    for req in action_requests:
        if req.get("name") == "execute_sql_query":
            args = req.get("args") or {}
            proposed_sql = args.get("sql") or ""
            nl_query = args.get("nl_query") or ""
            return AgentEvent(
                type=EventType.INTERRUPT,
                proposed_sql=proposed_sql if proposed_sql else None,
                nl_query=nl_query if nl_query else None,
            )
    return None


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
    * When the graph emits __interrupt__ (HITL), yields INTERRUPT with proposed_sql and nl_query.
    * Mutates `full_response_parts` so the caller can persist the response.
    """
    token_buffer: list[str] = []
    plan_emitted = False

    async for lc_event in graph_stream:
        kind: str = lc_event.get("event", "")

        hitl = _extract_interrupt_payload(lc_event)
        if hitl is not None:
            interrupt_evt = _interrupt_to_agent_event(hitl)
            if interrupt_evt is not None:
                yield interrupt_evt
            continue

        if kind == "on_chat_model_stream":
            chunk = lc_event.get("data", {}).get("chunk")
            if chunk and getattr(chunk, "content", None):
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

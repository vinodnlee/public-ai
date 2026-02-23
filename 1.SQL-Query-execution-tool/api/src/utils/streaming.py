"""Streaming utilities for parsing and yielding agent events."""

from collections.abc import Sequence
from typing import Any, AsyncIterator, AsyncGenerator
from src.agent.events import AgentEvent, EventType
from src.log import get_logger

logger = get_logger(__name__)


def _preview_text(val: Any, limit: int = 200) -> str:
    """Return a single-line preview for logs."""
    if not isinstance(val, str):
        return ""
    one_line = " ".join(val.split())
    if len(one_line) <= limit:
        return one_line
    return f"{one_line[:limit]}..."


def _extract_model_reply(lc_event: dict[str, Any]) -> tuple[str, list[Any]]:
    """Extract model text + tool calls from on_chat_model_end payload."""
    data = lc_event.get("data") or {}
    output = data.get("output")

    if output is None:
        return "", []

    content = getattr(output, "content", "")
    tool_calls = getattr(output, "tool_calls", None) or []

    if isinstance(output, dict):
        content = output.get("content", content)
        tool_calls = output.get("tool_calls", tool_calls) or []

    # Some providers store tool calls in additional kwargs.
    addl = getattr(output, "additional_kwargs", None) or {}
    if isinstance(addl, dict) and not tool_calls:
        tool_calls = addl.get("tool_calls") or []

    return _preview_text(content), tool_calls if isinstance(tool_calls, list) else []


def _coerce_hitl_request(val: Any) -> dict[str, Any] | None:
    """Best-effort conversion of LangGraph interrupt payload to HITLRequest dict."""
    if isinstance(val, dict):
        return val

    # langgraph emits __interrupt__ as a tuple/list of Interrupt objects.
    if isinstance(val, Sequence) and not isinstance(val, (str, bytes)):
        for item in val:
            # Interrupt(value=...) objects expose .value
            payload = getattr(item, "value", None)
            if isinstance(payload, dict):
                return payload
            if isinstance(item, dict):
                return item
        return None

    # Defensive: in case caller gives one Interrupt object directly.
    payload = getattr(val, "value", None)
    return payload if isinstance(payload, dict) else None


def _find_interrupt_value(obj: Any, depth: int = 0) -> Any | None:
    """Recursively search for a __interrupt__ value in nested event payloads."""
    if depth > 8:
        return None

    if isinstance(obj, dict):
        if "__interrupt__" in obj:
            return obj["__interrupt__"]
        for v in obj.values():
            found = _find_interrupt_value(v, depth + 1)
            if found is not None:
                return found
        return None

    if isinstance(obj, Sequence) and not isinstance(obj, (str, bytes)):
        for item in obj:
            found = _find_interrupt_value(item, depth + 1)
            if found is not None:
                return found
        return None

    # Objects like Interrupt may have nested value payloads.
    payload = getattr(obj, "value", None)
    if payload is not None:
        return _find_interrupt_value(payload, depth + 1)
    return None


def _extract_interrupt_payload(lc_event: dict) -> dict[str, Any] | None:
    """Return HITLRequest dict if this event carries __interrupt__, else None."""
    interrupt = _find_interrupt_value(lc_event)
    if interrupt is None:
        return None
    return _coerce_hitl_request(interrupt)


def _interrupt_to_agent_event(hitl_request: dict[str, Any]) -> AgentEvent | None:
    """Build an INTERRUPT AgentEvent from a HITLRequest action request.

    We prefer requests targeting execute_sql_query, but accept any request that
    carries SQL-like args to stay compatible with tool-name wrapping/aliasing.
    """
    action_requests = hitl_request.get("action_requests") or []
    candidate: dict[str, Any] | None = None

    for req in action_requests:
        if not isinstance(req, dict):
            continue
        name = str(req.get("name") or "")
        args = req.get("args") or {}
        if not isinstance(args, dict):
            continue

        if "execute_sql_query" in name:
            proposed_sql = args.get("sql") or ""
            nl_query = args.get("nl_query") or ""
            return AgentEvent(
                type=EventType.INTERRUPT,
                proposed_sql=proposed_sql if proposed_sql else None,
                nl_query=nl_query if nl_query else None,
            )

        if "sql" in args and candidate is None:
            candidate = args

    if candidate is not None:
        proposed_sql = candidate.get("sql") or ""
        nl_query = candidate.get("nl_query") or ""
        return AgentEvent(
            type=EventType.INTERRUPT,
            proposed_sql=proposed_sql if proposed_sql else None,
            nl_query=nl_query if nl_query else None,
        )
    # Fallback: do not drop unknown interrupt payloads silently.
    return AgentEvent(
        type=EventType.INTERRUPT,
        content="Human approval is required to continue.",
    )


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
            logger.info(
                "HITL interrupt detected | keys=%s",
                list(hitl.keys()) if isinstance(hitl, dict) else [],
            )
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

        elif kind == "on_chat_model_end":
            text_preview, tool_calls = _extract_model_reply(lc_event)
            tool_names = [
                str(tc.get("name")) for tc in tool_calls if isinstance(tc, dict) and tc.get("name")
            ]
            logger.info(
                "Model reply end | text=%s | tool_calls=%d | tool_names=%s",
                text_preview if text_preview else "<empty>",
                len(tool_calls),
                tool_names,
            )

    # Flush remaining tokens as the final ANSWER
    if token_buffer:
        answer_text = "".join(token_buffer).strip()
        if answer_text:
            yield AgentEvent(type=EventType.ANSWER, content=answer_text)
        token_buffer.clear()

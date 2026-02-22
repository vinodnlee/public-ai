"""
Tests for stream_agent_events — plan/answer/tool events and interrupt handling.
"""

import asyncio
from unittest.mock import AsyncMock

import pytest

from src.agent.events import AgentEvent, EventType
from src.utils.streaming import stream_agent_events


async def _collect(stream):
    return [e async for e in stream]


@pytest.mark.asyncio
async def test_stream_yields_interrupt_event_when_stream_contains_interrupt():
    """When graph stream has an event with __interrupt__ (HITLRequest), yield INTERRUPT AgentEvent."""
    hitl_payload = {
        "action_requests": [
            {
                "name": "execute_sql_query",
                "args": {"nl_query": "How many users?", "sql": "SELECT COUNT(*) FROM users"},
                "description": "Tool execution requires approval",
            }
        ],
        "review_configs": [{"action_name": "execute_sql_query", "allowed_decisions": ["approve", "edit", "reject"]}],
    }

    async def mock_stream():
        yield {"event": "on_chat_model_stream", "data": {"chunk": type("C", (), {"content": "Thinking..."})()}}
        yield {"event": "on_tool_start", "name": "task"}
        # Simulate LangGraph emitting interrupt (e.g. from tool or chain end)
        yield {"event": "on_chain_end", "data": {"output": {"__interrupt__": hitl_payload}}}

    captured: list[AgentEvent] = []
    full_parts: list[str] = []
    out = []
    async for evt in stream_agent_events(mock_stream(), "How many users?", captured, full_parts):
        out.append(evt)

    interrupt_events = [e for e in out if e.type == EventType.INTERRUPT]
    assert len(interrupt_events) == 1
    assert interrupt_events[0].proposed_sql == "SELECT COUNT(*) FROM users"
    assert interrupt_events[0].nl_query == "How many users?"

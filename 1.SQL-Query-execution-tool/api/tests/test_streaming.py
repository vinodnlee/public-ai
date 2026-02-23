"""
Tests for stream_agent_events — plan/answer/tool events and interrupt handling.
"""

import asyncio
from unittest.mock import AsyncMock

import pytest
from langgraph.types import Interrupt

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


@pytest.mark.asyncio
async def test_stream_yields_interrupt_when_payload_is_interrupt_tuple():
    """LangGraph interrupt payload may be a tuple/list of Interrupt objects."""
    hitl_payload = {
        "action_requests": [
            {
                "name": "execute_sql_query",
                "args": {"nl_query": "Users by dept", "sql": "SELECT department_id, COUNT(*) FROM users GROUP BY department_id"},
            }
        ]
    }

    async def mock_stream():
        yield {
            "event": "on_chain_end",
            "data": {"output": {"__interrupt__": (Interrupt(value=hitl_payload, id="it-1"),)}},
        }

    out = [e async for e in stream_agent_events(mock_stream(), "Users by dept", [], [])]
    interrupt_events = [e for e in out if e.type == EventType.INTERRUPT]
    assert len(interrupt_events) == 1
    assert interrupt_events[0].proposed_sql == "SELECT department_id, COUNT(*) FROM users GROUP BY department_id"
    assert interrupt_events[0].nl_query == "Users by dept"


@pytest.mark.asyncio
async def test_stream_yields_interrupt_when_tool_name_is_wrapped_alias():
    """Some runtimes may wrap tool names; interrupt parsing should still work."""
    hitl_payload = {
        "action_requests": [
            {
                "name": "sql_executor.execute_sql_query.v1",
                "args": {"nl_query": "dept counts", "sql": "SELECT d, COUNT(*) FROM t GROUP BY d"},
            }
        ]
    }

    async def mock_stream():
        yield {"event": "on_chain_end", "data": {"output": {"__interrupt__": hitl_payload}}}

    out = [e async for e in stream_agent_events(mock_stream(), "dept counts", [], [])]
    interrupt_events = [e for e in out if e.type == EventType.INTERRUPT]
    assert len(interrupt_events) == 1
    assert interrupt_events[0].proposed_sql == "SELECT d, COUNT(*) FROM t GROUP BY d"


@pytest.mark.asyncio
async def test_stream_keeps_unknown_interrupt_payload_instead_of_dropping():
    """Unknown interrupt payload shape should still yield an INTERRUPT event."""
    hitl_payload = {"foo": "bar"}

    async def mock_stream():
        yield {"event": "on_chain_end", "data": {"output": {"__interrupt__": hitl_payload}}}

    out = [e async for e in stream_agent_events(mock_stream(), "q", [], [])]
    interrupt_events = [e for e in out if e.type == EventType.INTERRUPT]
    assert len(interrupt_events) == 1


@pytest.mark.asyncio
async def test_stream_finds_interrupt_in_deep_nested_payload():
    """Interrupt may be nested in chunk/state payloads; parser should still find it."""
    hitl_payload = {
        "action_requests": [
            {"name": "execute_sql_query", "args": {"nl_query": "q", "sql": "SELECT 1"}}
        ]
    }

    async def mock_stream():
        yield {
            "event": "on_chain_stream",
            "data": {
                "chunk": {
                    "state": {
                        "__interrupt__": hitl_payload
                    }
                }
            },
        }

    out = [e async for e in stream_agent_events(mock_stream(), "q", [], [])]
    interrupt_events = [e for e in out if e.type == EventType.INTERRUPT]
    assert len(interrupt_events) == 1
    assert interrupt_events[0].proposed_sql == "SELECT 1"

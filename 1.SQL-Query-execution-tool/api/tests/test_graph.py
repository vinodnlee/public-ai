"""
Integration test for the DeepAgent supervisor graph.

Requires a running PostgreSQL instance and valid LLM API key.
Skipped automatically if database connection fails.

Usage:
    pytest tests/test_graph.py -v -s
"""

import asyncio

import pytest

from src.agent.deepagent_builder import build_supervisor_graph
from src.agent.events import AgentEvent
from src.db.adapters import get_adapter
from src.semantic.layer import SemanticLayer
from langgraph.checkpoint.memory import InMemorySaver


@pytest.fixture
async def adapter():
    """Create and connect a database adapter, disconnect on teardown."""
    a = get_adapter()
    await a.connect()
    yield a
    await a.disconnect()


@pytest.mark.asyncio
async def test_build_supervisor_graph(adapter):
    """Verify that the supervisor graph compiles without errors."""
    sem = SemanticLayer(adapter)
    events: list[AgentEvent] = []
    ckpt = InMemorySaver()

    graph = build_supervisor_graph(adapter, sem, events, ckpt)

    assert graph is not None
    assert hasattr(graph, "astream_events")


@pytest.mark.asyncio
async def test_graph_end_to_end(adapter):
    """Run a simple query through the graph and verify streaming output."""
    sem = SemanticLayer(adapter)
    events: list[AgentEvent] = []
    ckpt = InMemorySaver()

    graph = build_supervisor_graph(adapter, sem, events, ckpt)
    config = {"configurable": {"thread_id": "test-123"}}
    inp = {"messages": [
        {"role": "user", "content": "Show me all departments"}]}

    output_events = []
    async for event in graph.astream_events(inp, config=config, version="v2"):
        output_events.append(event)

    assert len(output_events) > 0, "Expected at least one streaming event"

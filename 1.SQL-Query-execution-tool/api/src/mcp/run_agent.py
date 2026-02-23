"""
Run the DeepAgent once and collect the final answer string.

Used by the MCP server tool query_database(question) -> str.
"""

import uuid

from src.agent.deep_agent import DeepAgent
from src.agent.events import EventType
from src.db.adapters.factory import get_adapter


async def run_agent_and_collect(question: str) -> str:
    """
    Run the supervisor with a fresh session, consume all events, return the answer.

    Collects ANSWER content and optional RESULT summaries. On INTERRUPT (HITL),
    returns a message directing the user to the web UI.
    """
    adapter = get_adapter()
    agent = DeepAgent(adapter)
    session_id = uuid.uuid4().hex
    parts: list[str] = []

    async for event in agent.run(question, session_id):
        if event.type == EventType.ANSWER and event.content:
            parts.append(event.content)
        elif event.type == EventType.RESULT and event.row_count is not None:
            parts.append(f"\n(Query returned {event.row_count} rows.)")
        elif event.type == EventType.INTERRUPT:
            return (
                "This query requires human approval. Please use the web UI to approve and run."
            )
        elif event.type == EventType.ERROR and event.content:
            return f"Error: {event.content}"

    return "".join(parts).strip() or "No response generated."

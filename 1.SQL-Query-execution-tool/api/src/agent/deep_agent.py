import uuid
from typing import AsyncGenerator

from langgraph.checkpoint.memory import InMemorySaver  # type: ignore

from src.log import get_logger
from src.agent.deepagent_builder import build_supervisor_graph
from src.agent.events import AgentEvent
from src.config.settings import get_settings
from src.db.adapters.base import DatabaseAdapter
from src.semantic.layer import SemanticLayer
from src.utils.streaming import stream_agent_events
from src.utils.history import build_chat_messages, save_chat_response

logger = get_logger(__name__)
settings = get_settings()


class DeepAgent:
    """Supervisor orchestrator."""

    def __init__(self, adapter: DatabaseAdapter) -> None:
        self._adapter = adapter
        self._semantic_layer = SemanticLayer(adapter)
        self._checkpointer = InMemorySaver()
        self._captured_events: list[AgentEvent] = []
        self._thread_map: dict[str, str] = {}
        logger.info("DeepAgent initialised | dialect=%s", adapter.dialect)

    async def run(
        self, query: str, session_id: str
    ) -> AsyncGenerator[AgentEvent, None]:
        """Run the supervisor pipeline and yield AgentEvents via SSE."""
        if session_id not in self._thread_map:
            self._thread_map[session_id] = uuid.uuid4().hex
        thread_id = self._thread_map[session_id]
        logger.info("run | session=%s thread=%s query=%s",
                    session_id, thread_id, query[:80])

        graph = build_supervisor_graph(
            self._adapter,
            self._semantic_layer,
            self._captured_events,
            self._checkpointer,
        )

        messages = await build_chat_messages(session_id, query)

        config = {"configurable": {"thread_id": thread_id}}
        input_payload = {"messages": messages}
        full_response_parts: list[str] = []

        graph_stream = graph.astream_events(
            input_payload, config=config, version="v2")

        async for event in stream_agent_events(
            graph_stream, query, self._captured_events, full_response_parts
        ):
            yield event

        full_response = "".join(full_response_parts)
        await save_chat_response(session_id, messages, full_response)
        logger.info("run complete | session=%s response_len=%d",
                    session_id, len(full_response))

        yield AgentEvent(type=EventType.DONE)

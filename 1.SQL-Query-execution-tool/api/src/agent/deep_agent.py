import uuid
from typing import Any, AsyncGenerator

from langgraph.types import Command

from src.log import get_logger
from src.agent.checkpointer import get_checkpointer
from src.agent.deepagent_builder import build_supervisor_graph
from src.agent.events import AgentEvent, EventType
from src.config.settings import get_settings
from src.db.adapters.base import DatabaseAdapter
from src.semantic.layer import SemanticLayer
from src.utils.streaming import stream_agent_events
from src.utils.history import build_chat_messages, save_chat_response
from src.cache.redis_client import get_session_history

logger = get_logger(__name__)
settings = get_settings()


class DeepAgent:
    """Supervisor orchestrator."""

    def __init__(self, adapter: DatabaseAdapter) -> None:
        self._adapter = adapter
        self._semantic_layer = SemanticLayer(adapter)
        self._checkpointer = get_checkpointer(settings)
        self._captured_events: list[AgentEvent] = []
        self._thread_map: dict[str, str] = {}
        self._reject_counts: dict[str, int] = {}
        self._session_last_query: dict[str, str] = {}
        logger.info("DeepAgent initialised | dialect=%s", adapter.dialect)

    async def run(
        self,
        query: str,
        session_id: str,
        runtime_config: dict[str, list[str]] | None = None,
    ) -> AsyncGenerator[AgentEvent, None]:
        """Run the supervisor pipeline and yield AgentEvents via SSE."""
        if session_id not in self._thread_map:
            self._thread_map[session_id] = uuid.uuid4().hex
        thread_id = self._thread_map[session_id]
        self._session_last_query[session_id] = query
        self._reject_counts[thread_id] = 0
        logger.info("run | session=%s thread=%s query=%s",
                    session_id, thread_id, query[:80])

        graph = build_supervisor_graph(
            self._adapter,
            self._semantic_layer,
            self._captured_events,
            self._checkpointer,
            runtime_config=runtime_config,
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
            if event.type == EventType.INTERRUPT:
                event = AgentEvent(
                    type=EventType.INTERRUPT,
                    proposed_sql=event.proposed_sql,
                    nl_query=event.nl_query,
                    thread_id=thread_id,
                )
            yield event

        full_response = "".join(full_response_parts)
        await save_chat_response(session_id, messages, full_response)
        logger.info("run complete | session=%s response_len=%d",
                    session_id, len(full_response))

        yield AgentEvent(type=EventType.DONE)

    async def resume(
        self,
        thread_id: str,
        session_id: str,
        decisions: list[dict[str, Any]],
        runtime_config: dict[str, list[str]] | None = None,
    ) -> AsyncGenerator[AgentEvent, None]:
        """Resume the graph after HITL interrupt; yield continuation events."""
        logger.info("resume | session=%s thread=%s", session_id, thread_id)

        # Allow limited replans on reject before bailing out.
        if decisions and all(d.get("type") == "reject" for d in decisions):
            count = self._reject_counts.get(thread_id, 0) + 1
            self._reject_counts[thread_id] = count
            max_replans = getattr(settings, "hitl_max_replans", 5)
            if count > max_replans:
                msg = (
                    f"SQL execution was rejected {count-1} times. "
                    "Max HITL replans reached; stopping."
                )
                yield AgentEvent(type=EventType.ANSWER, content=msg)
                yield AgentEvent(type=EventType.DONE)
                return
            logger.info("HITL reject #%d | thread=%s", count, thread_id)

            # Start a fresh planning pass with a new thread id.
            history = await get_session_history(session_id) or []
            original_query = next(
                (m.get("content") for m in reversed(history) if m.get("role") == "user"),
                None,
            ) or self._session_last_query.get(session_id)
            if not original_query:
                yield AgentEvent(
                    type=EventType.ANSWER,
                    content="Cannot replan: original query not found in session history.",
                )
                yield AgentEvent(type=EventType.DONE)
                return

            new_thread_id = uuid.uuid4().hex
            self._thread_map[session_id] = new_thread_id
            self._reject_counts[new_thread_id] = count  # carry over count

            graph = build_supervisor_graph(
                self._adapter,
                self._semantic_layer,
                self._captured_events,
                self._checkpointer,
                runtime_config=runtime_config,
            )
            messages = await build_chat_messages(session_id, original_query)
            config = {"configurable": {"thread_id": new_thread_id}}
            full_response_parts: list[str] = []

            graph_stream = graph.astream_events(
                {"messages": messages}, config=config, version="v2"
            )

            async for event in stream_agent_events(
                graph_stream, original_query, self._captured_events, full_response_parts
            ):
                if event.type == EventType.INTERRUPT:
                    event = AgentEvent(
                        type=EventType.INTERRUPT,
                        proposed_sql=event.proposed_sql,
                        nl_query=event.nl_query,
                        thread_id=new_thread_id,
                    )
                yield event

            full_response = "".join(full_response_parts)
            await save_chat_response(session_id, messages, full_response)
            yield AgentEvent(type=EventType.DONE)
            return

        graph = build_supervisor_graph(
            self._adapter,
            self._semantic_layer,
            self._captured_events,
            self._checkpointer,
            runtime_config=runtime_config,
        )
        config = {"configurable": {"thread_id": thread_id}}
        hitl_response = {"decisions": decisions}
        full_response_parts: list[str] = []

        graph_stream = graph.astream_events(
            Command(resume=hitl_response),
            config=config,
            version="v2",
        )

        async for event in stream_agent_events(
            graph_stream, "", self._captured_events, full_response_parts
        ):
            yield event

        yield AgentEvent(type=EventType.DONE)

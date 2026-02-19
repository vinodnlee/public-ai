import json
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from src.agent.deep_agent import DeepAgent
from src.api.schemas import ChatRequest, ChatInitResponse
from src.auth.jwt import get_current_user
from src.db.adapters.factory import get_adapter

router = APIRouter(prefix="/chat", tags=["chat"])

# Pending query store — maps stream_id → ChatRequest
# Use Redis in production for multi-process deployments.
_pending: dict[str, ChatRequest] = {}


@router.post("", response_model=ChatInitResponse)
async def initiate_chat(
    request: ChatRequest,
    _user: dict = Depends(get_current_user),
) -> JSONResponse:
    """
    Accept the user query.
    Returns a stream_url the UI opens via EventSource.
    """
    stream_id = str(uuid.uuid4())
    _pending[stream_id] = request
    return JSONResponse(
        content={
            "session_id": request.session_id,
            "stream_url": f"/api/chat/stream/{stream_id}",
        }
    )


@router.get("/stream/{stream_id}")
async def stream_chat(
    stream_id: str,
    request: Request,
    _user: dict = Depends(get_current_user),
) -> EventSourceResponse:
    """
    SSE endpoint — streams DeepAgent events (text/event-stream) to the UI.
    The adapter is resolved by the factory; no route knows which DB is used.
    """
    chat_request = _pending.pop(stream_id, None)
    if not chat_request:
        return EventSourceResponse(
            _error_stream("Invalid or expired stream ID"), status_code=404
        )

    adapter = get_adapter()
    agent = DeepAgent(adapter=adapter)

    async def event_generator():
        async for event in agent.run(
            query=chat_request.query,
            session_id=chat_request.session_id,
        ):
            if await request.is_disconnected():
                break
            yield {"data": json.dumps(event.model_dump(exclude_none=True))}

    return EventSourceResponse(event_generator())


async def _error_stream(message: str):
    yield {"data": json.dumps({"type": "error", "content": message})}

import json
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse
from src.agent.deep_agent import DeepAgent
from src.api.schemas import ChatRequest, ChatInitResponse
from src.auth.jwt import get_current_user
from src.cache.redis_client import get_redis
from src.db.adapters.factory import get_adapter

router = APIRouter(prefix="/chat", tags=["chat"])

_PENDING_TTL = 60   # seconds — stream must be opened within 60 s of POST
_CLAIMED_TTL = 30   # seconds — retry window after first connection attempt


async def _set_pending(stream_id: str, request: ChatRequest) -> None:
    redis = await get_redis()
    await redis.setex(f"pending:{stream_id}", _PENDING_TTL, request.model_dump_json())


async def _claim_pending(stream_id: str) -> ChatRequest | None:
    """
    Atomically move pending:{id} → claimed:{id}.
    First connection claims and copies to claimed key (short TTL for retries).
    Subsequent EventSource retries within _CLAIMED_TTL still succeed.
    """
    redis = await get_redis()
    pending_key = f"pending:{stream_id}"
    claimed_key = f"claimed:{stream_id}"

    # Check if already claimed (EventSource retry)
    data = await redis.get(claimed_key)
    if data:
        return ChatRequest.model_validate_json(data)

    # First hit: claim it
    data = await redis.getdel(pending_key)
    if data is None:
        return None

    # Store under claimed key for retry window
    await redis.setex(claimed_key, _CLAIMED_TTL, data)
    return ChatRequest.model_validate_json(data)


async def _delete_claimed(stream_id: str) -> None:
    redis = await get_redis()
    await redis.delete(f"claimed:{stream_id}")


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
    await _set_pending(stream_id, request)
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
    chat_request = await _claim_pending(stream_id)
    if not chat_request:
        return EventSourceResponse(
            _error_stream("Invalid or expired stream ID"), status_code=404
        )

    adapter = get_adapter()
    agent = DeepAgent(adapter=adapter)

    async def event_generator():
        try:
            async for event in agent.run(
                query=chat_request.query,
                session_id=chat_request.session_id,
            ):
                if await request.is_disconnected():
                    break
                yield {"data": json.dumps(event.model_dump(exclude_none=True))}
        except Exception as exc:
            # Send a final error event so the UI knows why the stream stopped
            yield {"data": json.dumps({"type": "error", "content": str(exc)})}
        finally:
            # Clean up claimed key — no more retries needed
            await _delete_claimed(stream_id)

    return EventSourceResponse(
        event_generator(),
        headers={
            # Prevent any upstream proxy or browser from buffering SSE
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
        },
    )


async def _error_stream(message: str):
    yield {"data": json.dumps({"type": "error", "content": message})}

import json
import uuid
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
from src.log import get_logger
from src.agent.deep_agent import DeepAgent
from src.api.schemas import ChatRequest, ChatInitResponse
from src.auth.jwt import get_current_user
from src.cache.redis_client import get_redis
from src.db.adapters.factory import get_adapter

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

_PENDING_TTL = 60
_CLAIMED_TTL = 30


async def _set_pending(stream_id: str, request: ChatRequest) -> None:
    redis = await get_redis()
    await redis.setex(f"pending:{stream_id}", _PENDING_TTL, request.model_dump_json())


async def _claim_pending(stream_id: str) -> ChatRequest | None:
    """Atomically move pending → claimed. Supports EventSource retries."""
    redis = await get_redis()
    pending_key = f"pending:{stream_id}"
    claimed_key = f"claimed:{stream_id}"

    data = await redis.get(claimed_key)
    if data:
        return ChatRequest.model_validate_json(data)

    data = await redis.getdel(pending_key)
    if data is None:
        return None

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
    stream_id = str(uuid.uuid4())
    logger.info("Chat initiated | session=%s stream=%s", request.session_id, stream_id)
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
    chat_request = await _claim_pending(stream_id)
    if not chat_request:
        logger.warning("Invalid or expired stream_id=%s", stream_id)
        return EventSourceResponse(
            _error_stream("Invalid or expired stream ID"), status_code=404
        )

    logger.info("Streaming started | stream=%s session=%s", stream_id, chat_request.session_id)
    adapter = get_adapter()
    agent = DeepAgent(adapter=adapter)

    async def event_generator():
        try:
            async for event in agent.run(
                query=chat_request.query,
                session_id=chat_request.session_id,
            ):
                if await request.is_disconnected():
                    logger.info("Client disconnected | stream=%s", stream_id)
                    break
                yield {"data": json.dumps(event.model_dump(exclude_none=True))}
        except Exception as exc:
            logger.error("Stream error | stream=%s error=%s", stream_id, exc)
            yield {"data": json.dumps({"type": "error", "content": str(exc)})}
        finally:
            await _delete_claimed(stream_id)

    return EventSourceResponse(
        event_generator(),
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
    )


@router.post("/direct")
async def direct_chat(
    chat_request: ChatRequest,
    _user: dict = Depends(get_current_user),
) -> StreamingResponse:
    """
    Direct one-step chat endpoint. Best for testing in Swagger.
    Returns a stream of events immediately.
    """
    logger.info("Direct chat initiated | session=%s", chat_request.session_id)
    adapter = get_adapter()
    agent = DeepAgent(adapter=adapter)

    async def event_generator():
        try:
            async for event in agent.run(
                query=chat_request.query,
                session_id=chat_request.session_id,
            ):
                # Standard SSE format
                yield f"data: {json.dumps(event.model_dump(exclude_none=True))}\n\n"
        except Exception as exc:
            logger.error("Direct stream error | error=%s", exc)
            yield f"data: {json.dumps({'type': 'error', 'content': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(), 
        media_type="text/event-stream"
    )


async def _error_stream(message: str):
    yield {"data": json.dumps({"type": "error", "content": message})}

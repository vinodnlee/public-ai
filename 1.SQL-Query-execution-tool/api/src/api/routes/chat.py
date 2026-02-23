import json
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
from src.log import get_logger
from src.agent.deep_agent import DeepAgent
from src.api.schemas import (
    ApproveRequest,
    ApproveInitResponse,
    ChatRequest,
    ChatInitResponse,
)
from src.auth.jwt import get_current_user
from src.cache.redis_client import get_redis
from src.config.user_agent_config import get_user_agent_config
from src.db.adapters.factory import get_adapter

logger = get_logger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

_PENDING_TTL = 60
_CLAIMED_TTL = 30
_APPROVE_PENDING_TTL = 120
_APPROVE_CLAIMED_TTL = 60


async def _set_pending(stream_id: str, request: ChatRequest) -> None:
    redis = await get_redis()
    await redis.setex(f"pending:{stream_id}", _PENDING_TTL, request.model_dump_json())


def _normalize_list(values: list[str] | None) -> list[str]:
    if values is None:
        return []
    out: list[str] = []
    for v in values:
        s = str(v).strip()
        if s:
            out.append(s)
    return out


async def _resolve_runtime_config(
    user_sub: str,
    selected_skills: list[str] | None,
    selected_skill_dirs: list[str] | None,
    selected_mcp_servers: list[str] | None,
) -> dict[str, list[str]]:
    base = await get_user_agent_config(user_sub)
    return {
        "enabled_skills": (
            _normalize_list(selected_skills)
            if selected_skills is not None
            else _normalize_list(base.get("enabled_skills"))
        ),
        "skill_dirs": (
            _normalize_list(selected_skill_dirs)
            if selected_skill_dirs is not None
            else _normalize_list(base.get("skill_dirs"))
        ),
        "mcp_servers": (
            _normalize_list(selected_mcp_servers)
            if selected_mcp_servers is not None
            else _normalize_list(base.get("mcp_servers"))
        ),
    }


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


def _approve_decisions(body: ApproveRequest) -> list[dict[str, Any]]:
    """Build HITLResponse decisions list from ApproveRequest."""
    if body.action == "approve":
        return [{"type": "approve"}]
    if body.action == "reject":
        return [{"type": "reject", "message": "User rejected the SQL execution."}]
    if body.action == "edit" and body.edited_sql:
        return [
            {
                "type": "edit",
                "edited_action": {
                    "name": "execute_sql_query",
                    "args": {
                        "nl_query": body.nl_query or "",
                        "sql": body.edited_sql,
                    },
                },
            }
        ]
    return [{"type": "reject", "message": "Edit requested but no edited_sql provided."}]


async def _set_approve_pending(
    stream_id: str,
    thread_id: str,
    session_id: str,
    decisions: list[dict[str, Any]],
    runtime_config: dict[str, list[str]],
) -> None:
    redis = await get_redis()
    payload = json.dumps(
        {
            "thread_id": thread_id,
            "session_id": session_id,
            "decisions": decisions,
            "runtime_config": runtime_config,
        }
    )
    await redis.setex(f"approve_pending:{stream_id}", _APPROVE_PENDING_TTL, payload)


async def _claim_approve(
    stream_id: str,
) -> tuple[str, str, list[dict[str, Any]], dict[str, list[str]]] | None:
    """Atomically move approve_pending → approve_claimed. Returns (thread_id, session_id, decisions) or None."""
    redis = await get_redis()
    pending_key = f"approve_pending:{stream_id}"
    claimed_key = f"approve_claimed:{stream_id}"

    data = await redis.get(claimed_key)
    if data:
        obj = json.loads(data)
        return (
            obj["thread_id"],
            obj["session_id"],
            obj["decisions"],
            obj.get("runtime_config") or {},
        )

    data = await redis.getdel(pending_key)
    if data is None:
        return None

    await redis.setex(claimed_key, _APPROVE_CLAIMED_TTL, data)
    obj = json.loads(data)
    return (
        obj["thread_id"],
        obj["session_id"],
        obj["decisions"],
        obj.get("runtime_config") or {},
    )


async def _delete_approve_claimed(stream_id: str) -> None:
    redis = await get_redis()
    await redis.delete(f"approve_claimed:{stream_id}")


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


@router.post("/approve", response_model=ApproveInitResponse)
async def approve_chat(
    body: ApproveRequest,
    _user: dict = Depends(get_current_user),
) -> JSONResponse:
    """Resume after HITL interrupt. Returns a new stream_url to consume the continuation."""
    stream_id = str(uuid.uuid4())
    decisions = _approve_decisions(body)
    user_sub = str(_user.get("sub", "anonymous"))
    runtime_config = await _resolve_runtime_config(
        user_sub,
        body.selected_skills,
        body.selected_skill_dirs,
        body.selected_mcp_servers,
    )
    logger.info(
        "Approve requested | session=%s thread=%s action=%s stream=%s",
        body.session_id,
        body.thread_id,
        body.action,
        stream_id,
    )
    await _set_approve_pending(
        stream_id,
        body.thread_id,
        body.session_id,
        decisions,
        runtime_config,
    )
    return JSONResponse(
        content={"stream_url": f"/api/chat/stream/{stream_id}"},
    )


@router.get("/stream/{stream_id}")
async def stream_chat(
    stream_id: str,
    request: Request,
    _user: dict = Depends(get_current_user),
) -> EventSourceResponse:
    chat_request = await _claim_pending(stream_id)
    approve_payload = None if chat_request else await _claim_approve(stream_id)

    if not chat_request and not approve_payload:
        logger.warning("Invalid or expired stream_id=%s", stream_id)
        return EventSourceResponse(
            _error_stream("Invalid or expired stream ID"), status_code=404
        )

    adapter = get_adapter()
    agent = DeepAgent(adapter=adapter)

    async def event_generator():
        try:
            if chat_request:
                runtime_config = await _resolve_runtime_config(
                    str(_user.get("sub", "anonymous")),
                    chat_request.selected_skills,
                    chat_request.selected_skill_dirs,
                    chat_request.selected_mcp_servers,
                )
                logger.info(
                    "Streaming started | stream=%s session=%s",
                    stream_id,
                    chat_request.session_id,
                )
                async for event in agent.run(
                    query=chat_request.query,
                    session_id=chat_request.session_id,
                    runtime_config=runtime_config,
                ):
                    if await request.is_disconnected():
                        logger.info("Client disconnected | stream=%s", stream_id)
                        break
                    yield {"data": json.dumps(event.model_dump(exclude_none=True))}
            else:
                thread_id, session_id, decisions, runtime_config = approve_payload
                if not runtime_config:
                    runtime_config = await _resolve_runtime_config(
                        str(_user.get("sub", "anonymous")),
                        None,
                        None,
                        None,
                    )
                logger.info(
                    "Resume stream started | stream=%s session=%s thread=%s",
                    stream_id,
                    session_id,
                    thread_id,
                )
                async for event in agent.resume(
                    thread_id=thread_id,
                    session_id=session_id,
                    decisions=decisions,
                    runtime_config=runtime_config,
                ):
                    if await request.is_disconnected():
                        logger.info("Client disconnected | stream=%s", stream_id)
                        break
                    yield {"data": json.dumps(event.model_dump(exclude_none=True))}
        except Exception as exc:
            logger.error("Stream error | stream=%s error=%s", stream_id, exc)
            yield {"data": json.dumps({"type": "error", "content": str(exc)})}
        finally:
            if chat_request:
                await _delete_claimed(stream_id)
            else:
                await _delete_approve_claimed(stream_id)

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
            runtime_config = await _resolve_runtime_config(
                str(_user.get("sub", "anonymous")),
                chat_request.selected_skills,
                chat_request.selected_skill_dirs,
                chat_request.selected_mcp_servers,
            )
            async for event in agent.run(
                query=chat_request.query,
                session_id=chat_request.session_id,
                runtime_config=runtime_config,
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

import json
import hashlib
from typing import Any
import redis.asyncio as aioredis
from src.config.settings import get_settings

settings = get_settings()

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def get_cached_result(sql: str) -> dict[str, Any] | None:
    client = await get_redis()
    key = _make_key(sql)
    cached = await client.get(key)
    return json.loads(cached) if cached else None


async def set_cached_result(sql: str, result: dict[str, Any]) -> None:
    client = await get_redis()
    key = _make_key(sql)
    await client.setex(key, settings.redis_ttl_seconds, json.dumps(result))


async def get_session_history(session_id: str) -> list[dict] | None:
    client = await get_redis()
    data = await client.get(f"session:{session_id}")
    return json.loads(data) if data else None


async def set_session_history(session_id: str, history: list[dict]) -> None:
    client = await get_redis()
    await client.setex(
        f"session:{session_id}",
        settings.redis_ttl_seconds,
        json.dumps(history),
    )


def _make_key(sql: str) -> str:
    return "sql_cache:" + hashlib.sha256(sql.strip().lower().encode()).hexdigest()

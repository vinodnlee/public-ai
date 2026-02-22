import json
import hashlib
from typing import Any
import redis.asyncio as aioredis
from src.log import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

_redis: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        logger.info("Connecting to Redis at %s", settings.redis_url)
        _redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        logger.info("Closing Redis connection")
        await _redis.aclose()
        _redis = None


async def get_cached_result(sql: str) -> dict[str, Any] | None:
    client = await get_redis()
    key = _make_key(sql)
    cached = await client.get(key)
    if cached:
        logger.debug("Cache hit | key=%s", key[:32])
    return json.loads(cached) if cached else None


async def set_cached_result(sql: str, result: dict[str, Any]) -> None:
    client = await get_redis()
    key = _make_key(sql)
    await client.setex(key, settings.redis_ttl_seconds, json.dumps(result))
    logger.debug("Cache set | key=%s ttl=%ds", key[:32], settings.redis_ttl_seconds)


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
    logger.debug("Session history saved | session=%s messages=%d", session_id, len(history))


def _make_key(sql: str) -> str:
    return "sql_cache:" + hashlib.sha256(sql.strip().lower().encode()).hexdigest()

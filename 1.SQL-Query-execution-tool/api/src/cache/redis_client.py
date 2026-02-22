import json
import hashlib
from typing import Any, Union
import redis.asyncio as aioredis
from src.log import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()

class InMemoryCache:
    """Simple in-memory fallback for local development."""
    def __init__(self):
        self._data: dict[str, str] = {}
        logger.info("Using InMemoryCache fallback")

    async def get(self, key: str) -> str | None:
        return self._data.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        # TTL is ignored in this simple implementation
        self._data[key] = value

    async def delete(self, key: str) -> None:
        self._data.pop(key, None)

    async def getdel(self, key: str) -> str | None:
        return self._data.pop(key, None)

    async def ping(self) -> bool:
        return True

    async def aclose(self) -> None:
        self._data.clear()

_client: Union[aioredis.Redis, InMemoryCache, None] = None

async def get_redis() -> Union[aioredis.Redis, InMemoryCache]:
    global _client
    if _client is None:
        # If explicitly told to use in-memory or if we're local/development
        # and don't want to rely on an external Redis.
        if settings.redis_host.lower() == "inmemory" or (settings.app_env.lower() in ["local", "development"] and settings.redis_host == "localhost"):
            try:
                # Try real Redis first if it's localhost
                if settings.redis_host != "inmemory":
                    logger.info("Attempting to connect to Redis at %s", settings.redis_url)
                    real_redis = aioredis.from_url(
                        settings.redis_url,
                        encoding="utf-8",
                        decode_responses=True,
                        socket_connect_timeout=1
                    )
                    await real_redis.ping()
                    _client = real_redis
                    logger.info("Successfully connected to Redis.")
                else:
                    _client = InMemoryCache()
            except Exception as e:
                logger.warning("Redis connection failed (%s). Falling back to InMemoryCache.", e)
                _client = InMemoryCache()
        else:
            logger.info("Connecting to production Redis at %s", settings.redis_url)
            _client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
    return _client

async def close_redis() -> None:
    global _client
    if _client is not None:
        logger.info("Closing cache connection")
        await _client.aclose()
        _client = None

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

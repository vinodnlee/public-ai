"""
Checkpointer factory: returns InMemorySaver or RedisSaver based on config.
"""

from typing import Any

from langgraph.checkpoint.memory import InMemorySaver  # type: ignore

from src.log import get_logger

logger = get_logger(__name__)
_CACHED_CHECKPOINTER: Any | None = None
_CACHED_KEY: tuple[str, str] | None = None


def get_checkpointer(settings: Any) -> Any:
    """Return a process-wide checkpointer instance keyed by config.

    Important for HITL resume: /run and /resume may create different DeepAgent
    instances in the same process, so they must share the same checkpointer.
    """
    global _CACHED_CHECKPOINTER, _CACHED_KEY

    cp_type = getattr(settings, "checkpointer_type", "memory")
    redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")
    key = (cp_type, redis_url)

    if _CACHED_CHECKPOINTER is not None and _CACHED_KEY == key:
        return _CACHED_CHECKPOINTER

    if cp_type == "redis":
        try:
            from langgraph_checkpoint_redis import RedisSaver  # type: ignore
            logger.info("Using Redis checkpointer | url=%s", redis_url.split("@")[-1] if "@" in redis_url else redis_url)
            _CACHED_CHECKPOINTER = RedisSaver.from_conn_string(redis_url)
            _CACHED_KEY = key
            return _CACHED_CHECKPOINTER
        except ImportError as e:
            logger.warning("Redis checkpointer requested but langgraph-checkpoint-redis not installed: %s; using memory", e)

    _CACHED_CHECKPOINTER = InMemorySaver()
    _CACHED_KEY = key
    return _CACHED_CHECKPOINTER

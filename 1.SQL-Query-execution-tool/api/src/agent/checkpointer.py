"""
Checkpointer factory: returns InMemorySaver or RedisSaver based on config.
"""

from typing import Any

from langgraph.checkpoint.memory import InMemorySaver  # type: ignore

from src.log import get_logger

logger = get_logger(__name__)


def get_checkpointer(settings: Any) -> Any:
    """Return a checkpointer instance: RedisSaver if type is 'redis' and available, else InMemorySaver."""
    if getattr(settings, "checkpointer_type", "memory") == "redis":
        try:
            from langgraph_checkpoint_redis import RedisSaver  # type: ignore
            redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")
            logger.info("Using Redis checkpointer | url=%s", redis_url.split("@")[-1] if "@" in redis_url else redis_url)
            return RedisSaver.from_conn_string(redis_url)
        except ImportError as e:
            logger.warning("Redis checkpointer requested but langgraph-checkpoint-redis not installed: %s; using memory", e)
    return InMemorySaver()

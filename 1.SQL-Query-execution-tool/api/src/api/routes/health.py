from fastapi import APIRouter
from src.log import get_logger
from src.cache.redis_client import get_redis
from src.db.adapters.factory import get_adapter

logger = get_logger(__name__)
router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check() -> dict:
    adapter = get_adapter()
    status = {
        "api": "ok",
        "database": {"type": adapter.dialect, "status": "unknown"},
        "redis": "unknown",
    }

    try:
        ok = await adapter.ping()
        status["database"]["status"] = "ok" if ok else "unreachable"
    except Exception as exc:
        logger.error("Database health check failed: %s", exc)
        status["database"]["status"] = f"error: {exc}"

    try:
        client = await get_redis()
        await client.ping()
        status["redis"] = "ok"
    except Exception as exc:
        logger.error("Redis health check failed: %s", exc)
        status["redis"] = f"error: {exc}"

    logger.info("Health check | db=%s redis=%s", status["database"]["status"], status["redis"])
    return status

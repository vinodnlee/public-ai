"""Database utility functions."""

from src.log import get_logger
from src.db.adapters.base import DatabaseAdapter

logger = get_logger(__name__)


async def check_db_connection(adapter: DatabaseAdapter) -> None:
    """
    Verify that the database connection is alive by sending a ping.
    Raises an OSError if the ping fails.
    """
    logger.info("Pinging database to verify connection...")
    ok = await adapter.ping()
    if not ok:
        logger.error("Database ping failed on startup.")
        raise OSError(
            "Database connection failed. Please ensure your database is running "
            "(e.g. start with: docker compose -f deploy/docker-compose.local.yml up -d)."
        )
    logger.info("Database connection established successfully.")

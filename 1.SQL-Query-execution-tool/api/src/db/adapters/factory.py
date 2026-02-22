"""Adapter factory — returns the correct DatabaseAdapter based on DB_TYPE."""

from functools import lru_cache
from src.log import get_logger
from src.db.adapters.base import DatabaseAdapter

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_adapter() -> DatabaseAdapter:
    from src.config.settings import get_settings
    settings = get_settings()

    db_type = settings.db_type.lower()
    logger.info("Creating adapter | db_type=%s", db_type)

    match db_type:
        case "postgresql":
            from src.db.adapters.postgres import PostgreSQLAdapter
            return PostgreSQLAdapter(
                dsn=settings.postgres_dsn,
                pool_size=settings.postgres_pool_size,
                max_overflow=settings.postgres_max_overflow,
                echo=settings.app_env == "development",
            )
        case "mysql":
            from src.db.adapters.mysql import MySQLAdapter
            return MySQLAdapter(
                dsn=settings.mysql_dsn,
                pool_size=settings.mysql_pool_size,
                max_overflow=settings.mysql_max_overflow,
                echo=settings.app_env == "development",
            )
        case "sqlite":
            from src.db.adapters.sqlite import SQLiteAdapter
            return SQLiteAdapter(
                dsn=settings.sqlite_dsn,
                echo=settings.app_env == "development",
            )
        case _:
            raise ValueError(
                f"Unsupported DB_TYPE '{settings.db_type}'. "
                "Supported: postgresql | mysql | sqlite"
            )

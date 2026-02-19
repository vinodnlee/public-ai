"""
Adapter factory.

Reads DB_TYPE from settings and returns the correct DatabaseAdapter
implementation. Adding a new database only requires:
  1. Creating a new subclass of DatabaseAdapter
  2. Adding one entry in the match block below.
"""

from functools import lru_cache
from src.db.adapters.base import DatabaseAdapter


@lru_cache(maxsize=1)
def get_adapter() -> DatabaseAdapter:
    """
    Return a singleton DatabaseAdapter based on the DB_TYPE setting.

    Supported values: postgresql | mysql | sqlite
    """
    from src.config.settings import get_settings

    settings = get_settings()

    match settings.db_type.lower():
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

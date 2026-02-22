"""SQLite adapter using aiosqlite + SQLAlchemy."""

from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.log import get_logger
from src.db.adapters.base import DatabaseAdapter

logger = get_logger(__name__)


class SQLiteAdapter(DatabaseAdapter):

    def __init__(self, dsn: str, echo: bool = False) -> None:
        self._dsn = dsn
        self._echo = echo
        self._engine: AsyncEngine | None = None
        self._session_factory: sessionmaker | None = None

    async def connect(self) -> None:
        logger.info("Connecting to SQLite | dsn=%s", self._dsn)
        self._engine = create_async_engine(
            self._dsn, echo=self._echo, future=True,
            connect_args={"check_same_thread": False},
        )
        self._session_factory = sessionmaker(
            bind=self._engine, class_=AsyncSession,
            expire_on_commit=False, autoflush=False, autocommit=False,
        )

    async def disconnect(self) -> None:
        if self._engine:
            logger.info("Disconnecting from SQLite")
            await self._engine.dispose()
            self._engine = None

    async def ping(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    async def execute_query(self, sql: str) -> dict[str, Any]:
        self.verify_read_only(sql)
        logger.debug("Executing query | sql=%s", sql[:120])
        async with self._session_factory() as session:
            result = await session.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            logger.debug("Query complete | rows=%d", len(rows))
            return {"columns": columns, "rows": rows, "row_count": len(rows)}

    async def get_tables(self) -> list[str]:
        async with self._session_factory() as session:
            result = await session.execute(text(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            ))
            return [row[0] for row in result.fetchall()]

    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(text(f"PRAGMA table_info('{table_name}')"))
            # PRAGMA columns: cid, name, type, notnull, dflt_value, pk
            return [
                {
                    "column": row[1],
                    "type": row[2],
                    "nullable": "NO" if row[3] else "YES",
                    "default": row[4],
                }
                for row in result.fetchall()
            ]

    async def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(text(f"PRAGMA foreign_key_list('{table_name}')"))
            # PRAGMA columns: id, seq, table, from, to, ...
            return [
                {"column": row[3], "foreign_table": row[2], "foreign_column": row[4]}
                for row in result.fetchall()
            ]

    @property
    def dialect(self) -> str:
        return "sqlite"

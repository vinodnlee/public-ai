"""MySQL adapter using aiomysql + SQLAlchemy."""

from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.log import get_logger
from src.db.adapters.base import DatabaseAdapter

logger = get_logger(__name__)


class MySQLAdapter(DatabaseAdapter):

    def __init__(self, dsn: str, pool_size: int = 10, max_overflow: int = 20, echo: bool = False) -> None:
        self._dsn = dsn
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._echo = echo
        self._engine: AsyncEngine | None = None
        self._session_factory: sessionmaker | None = None

    async def connect(self) -> None:
        logger.info("Connecting to MySQL | pool_size=%d", self._pool_size)
        self._engine = create_async_engine(
            self._dsn, pool_size=self._pool_size, max_overflow=self._max_overflow,
            echo=self._echo, future=True,
        )
        self._session_factory = sessionmaker(
            bind=self._engine, class_=AsyncSession,
            expire_on_commit=False, autoflush=False, autocommit=False,
        )

    async def disconnect(self) -> None:
        if self._engine:
            logger.info("Disconnecting from MySQL")
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
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = DATABASE() AND table_type = 'BASE TABLE' "
                "ORDER BY table_name"
            ))
            return [row[0] for row in result.fetchall()]

    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT column_name, data_type, is_nullable, column_default "
                    "FROM information_schema.columns "
                    "WHERE table_schema = DATABASE() AND table_name = :table "
                    "ORDER BY ordinal_position"
                ),
                {"table": table_name},
            )
            return [
                {"column": r[0], "type": r[1], "nullable": r[2], "default": r[3]}
                for r in result.fetchall()
            ]

    async def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT column_name, referenced_table_name, referenced_column_name "
                    "FROM information_schema.key_column_usage "
                    "WHERE table_schema = DATABASE() AND table_name = :table "
                    "AND referenced_table_name IS NOT NULL"
                ),
                {"table": table_name},
            )
            return [
                {"column": r[0], "foreign_table": r[1], "foreign_column": r[2]}
                for r in result.fetchall()
            ]

    @property
    def dialect(self) -> str:
        return "mysql"

"""PostgreSQL adapter — production implementation using SQLAlchemy + asyncpg."""

from typing import Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import sessionmaker
from src.db.adapters.base import DatabaseAdapter


class PostgreSQLAdapter(DatabaseAdapter):
    """
    Full async PostgreSQL adapter.
    Uses SQLAlchemy (asyncio) + asyncpg driver under the hood.
    """

    def __init__(
        self,
        dsn: str,
        pool_size: int = 10,
        max_overflow: int = 20,
        echo: bool = False,
    ) -> None:
        self._dsn = dsn
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._echo = echo
        self._engine: AsyncEngine | None = None
        self._session_factory: sessionmaker | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        self._engine = create_async_engine(
            self._dsn,
            pool_size=self._pool_size,
            max_overflow=self._max_overflow,
            echo=self._echo,
            future=True,
        )
        self._session_factory = sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )

    async def disconnect(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None

    async def ping(self) -> bool:
        try:
            async with self._engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Query execution
    # ------------------------------------------------------------------

    async def execute_query(self, sql: str) -> dict[str, Any]:
        self._guard_select(sql)
        async with self._session_factory() as session:
            result = await session.execute(text(sql))
            columns = list(result.keys())
            rows = [dict(zip(columns, row)) for row in result.fetchall()]
            return {"columns": columns, "rows": rows, "row_count": len(rows)}

    # ------------------------------------------------------------------
    # Schema introspection
    # ------------------------------------------------------------------

    async def get_tables(self) -> list[str]:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                      AND table_type = 'BASE TABLE'
                    ORDER BY table_name
                    """
                )
            )
            return [row[0] for row in result.fetchall()]

    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    """
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = :table
                    ORDER BY ordinal_position
                    """
                ),
                {"table": table_name},
            )
            return [
                {
                    "column": row[0],
                    "type": row[1],
                    "nullable": row[2],
                    "default": row[3],
                }
                for row in result.fetchall()
            ]

    async def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        async with self._session_factory() as session:
            result = await session.execute(
                text(
                    """
                    SELECT
                        kcu.column_name,
                        ccu.table_name  AS foreign_table,
                        ccu.column_name AS foreign_column
                    FROM information_schema.table_constraints AS tc
                    JOIN information_schema.key_column_usage AS kcu
                        ON tc.constraint_name = kcu.constraint_name
                    JOIN information_schema.constraint_column_usage AS ccu
                        ON ccu.constraint_name = tc.constraint_name
                    WHERE tc.constraint_type = 'FOREIGN KEY'
                      AND tc.table_name = :table
                    """
                ),
                {"table": table_name},
            )
            return [
                {
                    "column": row[0],
                    "foreign_table": row[1],
                    "foreign_column": row[2],
                }
                for row in result.fetchall()
            ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def dialect(self) -> str:
        return "postgresql"

    def get_engine(self) -> AsyncEngine:
        """Expose engine for direct Depends() injection in FastAPI if needed."""
        if self._engine is None:
            raise RuntimeError("Adapter not connected. Call connect() first.")
        return self._engine

    def get_session(self) -> AsyncSession:
        if self._session_factory is None:
            raise RuntimeError("Adapter not connected. Call connect() first.")
        return self._session_factory()

    @staticmethod
    def _guard_select(sql: str) -> None:
        if not sql.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT statements are permitted.")

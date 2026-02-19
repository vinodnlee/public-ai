"""
Abstract database adapter interface.

All database implementations must implement this interface so the rest of
the application remains completely database-agnostic.
"""

from abc import ABC, abstractmethod
from typing import Any


class DatabaseAdapter(ABC):
    """
    Generic database adapter interface.

    Implement this class to add support for any relational database.
    The application layer works exclusively against this interface —
    no database-specific code leaks beyond the adapters package.
    """

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    async def connect(self) -> None:
        """Initialise connection pool / engine."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close all connections and release resources."""

    @abstractmethod
    async def ping(self) -> bool:
        """Return True if the database is reachable."""

    # ------------------------------------------------------------------
    # Query execution
    # ------------------------------------------------------------------

    @abstractmethod
    async def execute_query(self, sql: str) -> dict[str, Any]:
        """
        Execute a read-only SELECT query.

        Returns:
            {
                "columns": list[str],
                "rows":    list[dict[str, Any]],
                "row_count": int,
            }

        Raises:
            ValueError: if the statement is not a SELECT.
            RuntimeError: on database execution errors.
        """

    # ------------------------------------------------------------------
    # Schema introspection
    # ------------------------------------------------------------------

    @abstractmethod
    async def get_tables(self) -> list[str]:
        """Return all user-accessible table names."""

    @abstractmethod
    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        """
        Return column metadata for a table.

        Each entry:
            {
                "column":   str,
                "type":     str,
                "nullable": str,   # "YES" | "NO"
                "default":  str | None,
            }
        """

    @abstractmethod
    async def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        """
        Return foreign key relationships for a table.

        Each entry:
            {
                "column":            str,
                "foreign_table":     str,
                "foreign_column":    str,
            }
        """

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def dialect(self) -> str:
        """Human-readable identifier, e.g. 'postgresql', 'mysql', 'sqlite'."""

    async def get_schema_context(self) -> str:
        """
        Return a formatted schema string suitable for injection into an LLM prompt.
        Default implementation builds from get_tables / get_columns / get_foreign_keys.
        Adapters may override this to provide richer output.
        """
        tables = await self.get_tables()
        lines: list[str] = [f"Database dialect: {self.dialect}\n\nSchema:\n"]
        for table in tables:
            columns = await self.get_columns(table)
            fks = {fk["column"]: fk for fk in await self.get_foreign_keys(table)}
            lines.append(f"Table: {table}")
            for col in columns:
                nullable = "NULL" if col["nullable"] == "YES" else "NOT NULL"
                fk_hint = ""
                if col["column"] in fks:
                    fk = fks[col["column"]]
                    fk_hint = f" → {fk['foreign_table']}.{fk['foreign_column']}"
                lines.append(
                    f"  - {col['column']} ({col['type']}, {nullable}){fk_hint}"
                )
            lines.append("")
        return "\n".join(lines)

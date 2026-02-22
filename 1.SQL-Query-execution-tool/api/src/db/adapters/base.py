"""Abstract database adapter interface."""

import re
from abc import ABC, abstractmethod
from typing import Any


class DatabaseAdapter(ABC):

    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def execute_query(self, sql: str) -> dict[str, Any]:
        """Execute a read-only SELECT. Returns {columns, rows, row_count}."""

    @abstractmethod
    async def get_tables(self) -> list[str]: ...

    @abstractmethod
    async def get_columns(self, table_name: str) -> list[dict[str, Any]]:
        """Return [{column, type, nullable, default}, ...]."""

    @abstractmethod
    async def get_foreign_keys(self, table_name: str) -> list[dict[str, Any]]:
        """Return [{column, foreign_table, foreign_column}, ...]."""

    @property
    @abstractmethod
    def dialect(self) -> str: ...

    def verify_read_only(self, sql: str) -> None:
        """Throw ValueError if the SQL contains mutating keywords."""
        sql_upper = sql.upper()
        # Only allow SELECT and WITH prefixes (ignoring leading whitespace/comments for a simple check)
        # More robust check: deny list of DML/DDL commands
        forbidden = [
            r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
            r"\bALTER\b", r"\bTRUNCATE\b", r"\bGRANT\b", r"\bREVOKE\b",
            r"\bEXEC\b", r"\bEXECUTE\b", r"\bCALL\b", r"\bREPLACE\b",
            r"\bCREATE\b", r"\bMERGE\b"
        ]
        
        for pattern in forbidden:
            if re.search(pattern, sql_upper):
                raise ValueError(f"Potentially unsafe SQL detected. Keyword matched: {pattern.replace(r'\b', '')}")

    async def get_schema_context(self) -> str:
        """Build a formatted schema string for LLM prompt injection."""
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

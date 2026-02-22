"""Semantic layer — merges raw DB schema with business-level descriptions."""

from src.log import get_logger
from src.db.adapters.base import DatabaseAdapter
from src.semantic.models import SemanticTable
from src.semantic.registry import SemanticRegistry, get_default_registry

logger = get_logger(__name__)


class SemanticLayer:

    def __init__(self, adapter: DatabaseAdapter, registry: SemanticRegistry | None = None) -> None:
        self._adapter = adapter
        self._registry = registry or get_default_registry()

    async def build_prompt_context(self) -> str:
        """Build the full schema + semantic context string for LLM prompting."""
        physical_tables = await self._adapter.get_tables()
        logger.info("Building prompt context | tables=%d", len(physical_tables))
        sections: list[str] = [
            f"Database dialect: {self._adapter.dialect}\n",
            "=== DATABASE SCHEMA & SEMANTIC CONTEXT ===\n",
        ]

        for table_name in physical_tables:
            semantic = self._registry.get(table_name)
            if semantic:
                sections.append(self._build_semantic_section(table_name, semantic))
            else:
                sections.append(await self._build_raw_section(table_name))

        sections.append("\n=== END SCHEMA ===")
        return "\n".join(sections)

    async def enrich_table(self, table_name: str) -> dict:
        """Merged view of physical schema + semantic definitions for one table."""
        physical_columns = await self._adapter.get_columns(table_name)
        foreign_keys = await self._adapter.get_foreign_keys(table_name)
        fk_map = {fk["column"]: fk for fk in foreign_keys}
        semantic = self._registry.get(table_name)

        enriched_columns = []
        for col in physical_columns:
            sem_col = semantic.get_column(col["column"]) if semantic else None
            enriched_columns.append(
                {
                    "name":         col["column"],
                    "type":         col["type"],
                    "nullable":     col["nullable"],
                    "default":      col["default"],
                    "display_name": sem_col.display_name if sem_col else col["column"],
                    "description":  sem_col.description if sem_col else "",
                    "is_sensitive": sem_col.is_sensitive if sem_col else False,
                    "example_values": sem_col.example_values if sem_col else [],
                    "foreign_key":  fk_map.get(col["column"]),
                }
            )

        logger.debug("Enriched table=%s | columns=%d", table_name, len(enriched_columns))
        return {
            "table":        table_name,
            "display_name": semantic.display_name if semantic else table_name,
            "description":  semantic.description if semantic else "",
            "columns":      enriched_columns,
            "common_queries": semantic.common_queries if semantic else [],
            "joins":        semantic.joins if semantic else [],
        }

    async def list_tables(self) -> list[dict]:
        physical_tables = await self._adapter.get_tables()
        result = []
        for name in physical_tables:
            sem = self._registry.get(name)
            result.append(
                {
                    "name":         name,
                    "display_name": sem.display_name if sem else name,
                    "description":  sem.description if sem else "",
                    "has_semantic": sem is not None,
                }
            )
        return result

    def _build_semantic_section(self, table_name: str, semantic: SemanticTable) -> str:
        return semantic.to_prompt_fragment() + "\n"

    async def _build_raw_section(self, table_name: str) -> str:
        columns = await self._adapter.get_columns(table_name)
        fks = {fk["column"]: fk for fk in await self._adapter.get_foreign_keys(table_name)}
        lines = [f"Table: {table_name} [no semantic definition]"]
        for col in columns:
            nullable = "NULL" if col["nullable"] == "YES" else "NOT NULL"
            fk_hint = ""
            if col["column"] in fks:
                fk = fks[col["column"]]
                fk_hint = f" → {fk['foreign_table']}.{fk['foreign_column']}"
            lines.append(f"  - {col['column']} ({col['type']}, {nullable}){fk_hint}")
        return "\n".join(lines) + "\n"

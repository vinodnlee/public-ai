"""
Semantic layer.

Merges raw database schema (from any DatabaseAdapter) with
business-level descriptions (from SemanticRegistry) to produce
a rich, LLM-ready context string.

This is the single component the agent interacts with — it has
no knowledge of which database or which semantic definitions
are in use.
"""

from src.db.adapters.base import DatabaseAdapter
from src.semantic.models import SemanticTable
from src.semantic.registry import SemanticRegistry, get_default_registry


class SemanticLayer:
    """
    Combines physical schema metadata with semantic table/column descriptions.

    The output of build_prompt_context() is injected directly into the
    DeepAgent system prompt so the LLM understands:
      - what tables exist (physical schema)
      - what each table/column *means* (semantic description)
      - example queries (few-shot hints)
    """

    def __init__(
        self,
        adapter: DatabaseAdapter,
        registry: SemanticRegistry | None = None,
    ) -> None:
        self._adapter = adapter
        self._registry = registry or get_default_registry()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def build_prompt_context(self) -> str:
        """
        Build the full schema + semantic context string for LLM prompting.

        Strategy:
          1. Fetch all tables from the database via the adapter.
          2. For each table, check if the semantic registry has a definition.
             - If yes: use the rich semantic description to build the fragment.
             - If no:  fall back to raw schema column names + types.
          3. Concatenate everything into a single string.
        """
        physical_tables = await self._adapter.get_tables()
        sections: list[str] = [
            f"Database dialect: {self._adapter.dialect}\n",
            "=== DATABASE SCHEMA & SEMANTIC CONTEXT ===\n",
        ]

        for table_name in physical_tables:
            semantic = self._registry.get(table_name)
            if semantic:
                sections.append(
                    self._build_semantic_section(table_name, semantic))
            else:
                sections.append(await self._build_raw_section(table_name))

        sections.append("\n=== END SCHEMA ===")
        return "\n".join(sections)

    async def enrich_table(self, table_name: str) -> dict:
        """
        Return a merged view of the physical schema + semantic definitions
        for a single table. Used by the Schema Inspector API endpoint.
        """
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

        return {
            "table":        table_name,
            "display_name": semantic.display_name if semantic else table_name,
            "description":  semantic.description if semantic else "",
            "columns":      enriched_columns,
            "common_queries": semantic.common_queries if semantic else [],
            "joins":        semantic.joins if semantic else [],
        }

    async def list_tables(self) -> list[dict]:
        """Return a summary list of all tables with semantic display names."""
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

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_semantic_section(
        self, table_name: str, semantic: SemanticTable
    ) -> str:
        """Use rich semantic description when available."""
        return semantic.to_prompt_fragment() + "\n"

    async def _build_raw_section(self, table_name: str) -> str:
        """Fall back to raw physical schema when no semantic entry exists."""
        columns = await self._adapter.get_columns(table_name)
        fks = {fk["column"]: fk for fk in await self._adapter.get_foreign_keys(table_name)}
        lines = [f"Table: {table_name} [no semantic definition]"]
        for col in columns:
            nullable = "NULL" if col["nullable"] == "YES" else "NOT NULL"
            fk_hint = ""
            if col["column"] in fks:
                fk = fks[col["column"]]
                fk_hint = f" → {fk['foreign_table']}.{fk['foreign_column']}"
            lines.append(
                f"  - {col['column']} ({col['type']}, {nullable}){fk_hint}")
        return "\n".join(lines) + "\n"

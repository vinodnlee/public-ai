"""
Semantic layer data models.

These models describe the *business meaning* of database tables and columns
in plain language, allowing the LLM to understand context beyond raw SQL types.
"""

from pydantic import BaseModel, Field


class SemanticColumn(BaseModel):
    """Business-level description of a single database column."""

    name: str = Field(..., description="Physical column name in the database.")
    display_name: str = Field(...,
                              description="Human-friendly label shown in the UI.")
    description: str = Field(
        ..., description="Plain-English explanation of what this column represents."
    )
    example_values: list[str] = Field(
        default_factory=list,
        description="Optional sample values to help the LLM generate accurate queries.",
    )
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_sensitive: bool = Field(
        default=False,
        description="If True, remind the LLM not to expose raw values.",
    )


class SemanticTable(BaseModel):
    """Business-level description of a database table."""

    name: str = Field(..., description="Physical table name in the database.")
    display_name: str = Field(...,
                              description="Human-friendly label for the table.")
    description: str = Field(
        ..., description="What this table represents in the business domain."
    )
    columns: list[SemanticColumn] = Field(
        default_factory=list,
        description="Column-level semantic definitions.",
    )
    common_queries: list[str] = Field(
        default_factory=list,
        description="Example natural language queries commonly asked against this table.",
    )
    joins: list[str] = Field(
        default_factory=list,
        description="Tables this table is commonly joined with.",
    )

    def get_column(self, name: str) -> SemanticColumn | None:
        return next((c for c in self.columns if c.name == name), None)

    def to_prompt_fragment(self) -> str:
        """
        Render a compact prompt-friendly description for LLM injection.
        """
        lines = [
            f"Table: {self.name} ({self.display_name})",
            f"  Purpose: {self.description}",
        ]
        for col in self.columns:
            sensitivity = " [SENSITIVE]" if col.is_sensitive else ""
            examples = f"  e.g. {', '.join(col.example_values)}" if col.example_values else ""
            lines.append(
                f"  - {col.name}: {col.description}{sensitivity}{examples}"
            )
        if self.common_queries:
            lines.append("  Common questions:")
            for q in self.common_queries:
                lines.append(f"    • {q}")
        return "\n".join(lines)

"""Semantic layer data models."""

from pydantic import BaseModel, Field


class SemanticColumn(BaseModel):
    name: str
    display_name: str
    description: str
    example_values: list[str] = Field(default_factory=list)
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_sensitive: bool = False


class SemanticTable(BaseModel):
    name: str
    display_name: str
    description: str
    columns: list[SemanticColumn] = Field(default_factory=list)
    common_queries: list[str] = Field(default_factory=list)
    joins: list[str] = Field(default_factory=list)

    def get_column(self, name: str) -> SemanticColumn | None:
        return next((c for c in self.columns if c.name == name), None)

    def to_prompt_fragment(self) -> str:
        lines = [
            f"Table: {self.name} ({self.display_name})",
            f"  Purpose: {self.description}",
        ]
        for col in self.columns:
            sensitivity = " [SENSITIVE]" if col.is_sensitive else ""
            examples = f"  e.g. {', '.join(col.example_values)}" if col.example_values else ""
            lines.append(f"  - {col.name}: {col.description}{sensitivity}{examples}")
        if self.common_queries:
            lines.append("  Common questions:")
            for q in self.common_queries:
                lines.append(f"    • {q}")
        return "\n".join(lines)

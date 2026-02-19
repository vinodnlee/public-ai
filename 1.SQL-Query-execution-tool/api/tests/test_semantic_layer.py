"""
Tests for SemanticLayer: build_prompt_context, list_tables, enrich_table.
"""

import pytest
from src.semantic.layer import SemanticLayer
from src.semantic.registry import SemanticRegistry


@pytest.mark.asyncio
async def test_build_prompt_context_contains_dialect_and_tables(sqlite_adapter) -> None:
    layer = SemanticLayer(sqlite_adapter)
    ctx = await layer.build_prompt_context()
    assert "sqlite" in ctx.lower()
    assert "test_users" in ctx
    assert "DATABASE SCHEMA" in ctx or "schema" in ctx.lower()


@pytest.mark.asyncio
async def test_list_tables(sqlite_adapter) -> None:
    layer = SemanticLayer(sqlite_adapter)
    tables = await layer.list_tables()
    assert len(tables) >= 1
    names = [t["name"] for t in tables]
    assert "test_users" in names
    for t in tables:
        assert "name" in t and "display_name" in t and "has_semantic" in t


@pytest.mark.asyncio
async def test_enrich_table(sqlite_adapter) -> None:
    layer = SemanticLayer(sqlite_adapter)
    enriched = await layer.enrich_table("test_users")
    assert enriched["table"] == "test_users"
    assert "columns" in enriched
    assert len(enriched["columns"]) >= 2
    col_names = [c["name"] for c in enriched["columns"]]
    assert "id" in col_names and "name" in col_names


@pytest.mark.asyncio
async def test_build_prompt_context_with_semantic_registry(sqlite_adapter) -> None:
    """When registry has no entry for a table, raw schema is used."""
    registry = SemanticRegistry()
    layer = SemanticLayer(sqlite_adapter, registry=registry)
    ctx = await layer.build_prompt_context()
    assert "test_users" in ctx
    assert "no semantic definition" in ctx or "id" in ctx

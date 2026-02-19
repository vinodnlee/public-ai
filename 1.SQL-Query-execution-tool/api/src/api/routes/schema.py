"""
Schema browser API.

Exposes the semantic layer — enriched table/column metadata combining
physical schema (from the database adapter) with business descriptions
(from the semantic registry).  The UI can use this to build a schema
sidebar or column picker.
"""

from fastapi import APIRouter
from src.db.adapters.factory import get_adapter
from src.semantic.layer import SemanticLayer

router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("")
async def list_tables() -> list[dict]:
    """
    List all tables with their semantic display names and descriptions.
    """
    adapter = get_adapter()
    layer = SemanticLayer(adapter)
    return await layer.list_tables()


@router.get("/{table_name}")
async def get_table(table_name: str) -> dict:
    """
    Return enriched column metadata + semantic definitions for a single table.
    """
    adapter = get_adapter()
    layer = SemanticLayer(adapter)
    return await layer.enrich_table(table_name)


@router.get("/context/prompt")
async def get_prompt_context() -> dict:
    """
    Return the full schema context string used by DeepAgent in its system prompt.
    Useful for debugging what context the LLM sees.
    """
    adapter = get_adapter()
    layer = SemanticLayer(adapter)
    context = await layer.build_prompt_context()
    return {"dialect": adapter.dialect, "context": context}

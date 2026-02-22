"""Schema browser API."""

from fastapi import APIRouter, Depends
from src.log import get_logger
from src.auth.jwt import get_current_user
from src.db.adapters.factory import get_adapter
from src.semantic.layer import SemanticLayer

logger = get_logger(__name__)
router = APIRouter(prefix="/schema", tags=["schema"])


@router.get("")
async def list_tables(_user: dict = Depends(get_current_user)) -> list[dict]:
    adapter = get_adapter()
    layer = SemanticLayer(adapter)
    tables = await layer.list_tables()
    logger.info("Listed %d tables", len(tables))
    return tables


@router.get("/{table_name}")
async def get_table(
    table_name: str,
    _user: dict = Depends(get_current_user),
) -> dict:
    logger.info("Enriching table=%s", table_name)
    adapter = get_adapter()
    layer = SemanticLayer(adapter)
    return await layer.enrich_table(table_name)


@router.get("/context/prompt")
async def get_prompt_context(_user: dict = Depends(get_current_user)) -> dict:
    adapter = get_adapter()
    layer = SemanticLayer(adapter)
    context = await layer.build_prompt_context()
    logger.debug("Prompt context built | length=%d", len(context))
    return {"dialect": adapter.dialect, "context": context}

from langchain_core.tools import InjectedToolArg, tool
from typing_extensions import Annotated

from src.log import get_logger
from src.semantic.layer import SemanticLayer

logger = get_logger(__name__)


@tool(parse_docstring=True)
async def get_schema_context_tool(
    semantic_layer: Annotated[SemanticLayer, InjectedToolArg],
) -> str:
    """Return the full semantic + physical schema context for the LLM prompt.

    Args:
        semantic_layer: The semantic layer instance (injected at runtime).

    Returns:
        A formatted string describing the database schema.
    """
    logger.info("Building schema context")
    result = await semantic_layer.build_prompt_context()
    logger.debug("Schema context built | length=%d", len(result))
    return result

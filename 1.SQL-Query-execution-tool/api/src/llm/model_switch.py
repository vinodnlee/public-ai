"""
Dynamic model-switch middleware for LangChain agents.
"""

from __future__ import annotations

from typing import Any

from langchain.agents.middleware import ModelRequest, ModelResponse, wrap_model_call

from src.llm.llm_factory import get_llm
from src.log import get_logger

logger = get_logger(__name__)


def should_use_advanced_model(message_count: int, threshold: int) -> bool:
    """Return True when conversation length warrants advanced model."""
    return message_count > threshold


def build_dynamic_model_switch_middleware(settings: Any):
    """Build middleware that switches between lightweight and advanced model."""
    lightweight_model = get_llm(model=getattr(settings, "llm_lightweight_model", "gpt-4o-mini"))
    advanced_model = get_llm(model=getattr(settings, "llm_advanced_model", "gpt-4o"))
    threshold = int(getattr(settings, "model_switch_message_threshold", 12))

    @wrap_model_call
    def dynamic_model_switch(
        request: ModelRequest,
        handler,
    ) -> ModelResponse:
        message_count = len(request.messages or [])
        use_advanced = should_use_advanced_model(message_count, threshold)
        selected_model = advanced_model if use_advanced else lightweight_model
        selected_name = (
            getattr(settings, "llm_advanced_model", "advanced")
            if use_advanced
            else getattr(settings, "llm_lightweight_model", "lightweight")
        )
        logger.debug(
            "Dynamic model switch | messages=%d threshold=%d selected=%s",
            message_count,
            threshold,
            selected_name,
        )
        return handler(request.override(model=selected_model))

    return dynamic_model_switch

"""
Tests for checkpointer factory: memory vs redis (when available).
"""

from unittest.mock import MagicMock

from langgraph.checkpoint.memory import InMemorySaver

from src.agent.checkpointer import get_checkpointer


def test_get_checkpointer_memory_returns_in_memory_saver() -> None:
    """When checkpointer_type is memory, return InMemorySaver."""
    settings = MagicMock()
    settings.checkpointer_type = "memory"
    settings.redis_url = "redis://localhost:6379/0"
    cp = get_checkpointer(settings)
    assert isinstance(cp, InMemorySaver)


def test_get_checkpointer_default_is_memory() -> None:
    """When checkpointer_type is not set or not 'redis', return InMemorySaver."""
    settings = MagicMock()
    settings.checkpointer_type = "something_else"
    settings.redis_url = "redis://localhost:6379/0"
    cp = get_checkpointer(settings)
    assert isinstance(cp, InMemorySaver)


def test_get_checkpointer_reuses_singleton_for_same_config() -> None:
    """Same config should reuse one checkpointer instance (required by HITL resume)."""
    settings = MagicMock()
    settings.checkpointer_type = "memory"
    settings.redis_url = "redis://localhost:6379/0"
    cp1 = get_checkpointer(settings)
    cp2 = get_checkpointer(settings)
    assert cp1 is cp2

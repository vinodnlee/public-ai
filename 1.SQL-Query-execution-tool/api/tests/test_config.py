"""
Tests for config/settings — skill and MCP-related settings parsing.
"""

import os

import pytest

from src.config.settings import Settings, get_settings


def test_enabled_skills_default_is_empty_list() -> None:
    """Default enabled_skills should be an empty list."""
    # Instantiate without env override so we get defaults
    s = Settings()
    assert hasattr(s, "enabled_skills")
    assert s.enabled_skills == []


def test_enabled_skills_parses_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """ENABLED_SKILLS env var should be parsed into a list of strings."""
    monkeypatch.setenv("ENABLED_SKILLS", "export_csv,explain_language")
    s = Settings()
    assert s.enabled_skills == ["export_csv", "explain_language"]


def test_enabled_skills_strips_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    """ENABLED_SKILLS entries should be stripped of surrounding whitespace."""
    monkeypatch.setenv("ENABLED_SKILLS", "  a  ,  b  ")
    s = Settings()
    assert s.enabled_skills == ["a", "b"]


def test_skill_dirs_default_is_empty_list() -> None:
    """Default skill_dirs should be an empty list."""
    s = Settings()
    assert hasattr(s, "skill_dirs")
    assert s.skill_dirs == []


def test_skill_dirs_parses_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """SKILL_DIRS env var should be parsed into a list of paths."""
    monkeypatch.setenv("SKILL_DIRS", "/path/to/cursor/skills,/path/to/codex/skills")
    s = Settings()
    assert s.skill_dirs == ["/path/to/cursor/skills", "/path/to/codex/skills"]


def test_checkpointer_type_default_is_memory() -> None:
    """Default checkpointer_type should be 'memory'."""
    s = Settings()
    assert s.checkpointer_type == "memory"


def test_mcp_servers_default_is_empty_list() -> None:
    """Default mcp_servers should be an empty list."""
    s = Settings()
    assert s.mcp_servers == []


def test_mcp_servers_parses_comma_separated_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """MCP_SERVERS env var should be parsed into a list."""
    monkeypatch.setenv("MCP_SERVERS", "http://localhost:8080,stdio:node:server.js")
    s = Settings()
    assert "http://localhost:8080" in s.mcp_servers
    assert "stdio:node:server.js" in s.mcp_servers

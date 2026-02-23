from unittest.mock import AsyncMock, patch

import pytest

from src.api.routes.chat import _resolve_runtime_config


@pytest.mark.asyncio
async def test_resolve_runtime_config_uses_user_defaults_when_no_selection() -> None:
    with patch("src.api.routes.chat.get_user_agent_config", new_callable=AsyncMock) as m_get:
        m_get.return_value = {
            "enabled_skills": ["export_csv"],
            "skill_dirs": ["C:/skills"],
            "mcp_servers": ["http://localhost:9123/mcp"],
        }
        config = await _resolve_runtime_config(
            "user-1",
            None,
            None,
            None,
        )
        assert config["enabled_skills"] == ["export_csv"]
        assert config["skill_dirs"] == ["C:/skills"]
        assert config["mcp_servers"] == ["http://localhost:9123/mcp"]


@pytest.mark.asyncio
async def test_resolve_runtime_config_allows_explicit_empty_override() -> None:
    with patch("src.api.routes.chat.get_user_agent_config", new_callable=AsyncMock) as m_get:
        m_get.return_value = {
            "enabled_skills": ["export_csv"],
            "skill_dirs": ["C:/skills"],
            "mcp_servers": ["http://localhost:9123/mcp"],
        }
        config = await _resolve_runtime_config(
            "user-1",
            [],
            [],
            [],
        )
        assert config["enabled_skills"] == []
        assert config["skill_dirs"] == []
        assert config["mcp_servers"] == []

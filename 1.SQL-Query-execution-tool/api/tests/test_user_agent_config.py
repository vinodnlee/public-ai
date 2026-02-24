from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from src.config.user_agent_config import set_user_agent_config


@pytest.mark.asyncio
async def test_set_user_agent_config_persists_without_expiry_by_default() -> None:
    mock_redis = AsyncMock()
    with patch("src.config.user_agent_config.get_redis", new_callable=AsyncMock, return_value=mock_redis), \
         patch("src.config.user_agent_config.get_user_agent_config", new_callable=AsyncMock, return_value={
             "enabled_skills": [],
             "skill_dirs": [],
             "mcp_servers": [],
         }), \
         patch("src.config.user_agent_config.get_settings", return_value=SimpleNamespace(user_agent_config_ttl_seconds=0)):
        await set_user_agent_config("u1", enabled_skills=["export_csv"])

    mock_redis.set.assert_awaited_once()
    mock_redis.setex.assert_not_awaited()


@pytest.mark.asyncio
async def test_set_user_agent_config_uses_setex_when_ttl_configured() -> None:
    mock_redis = AsyncMock()
    with patch("src.config.user_agent_config.get_redis", new_callable=AsyncMock, return_value=mock_redis), \
         patch("src.config.user_agent_config.get_user_agent_config", new_callable=AsyncMock, return_value={
             "enabled_skills": [],
             "skill_dirs": [],
             "mcp_servers": [],
         }), \
         patch("src.config.user_agent_config.get_settings", return_value=SimpleNamespace(user_agent_config_ttl_seconds=86400)):
        await set_user_agent_config("u1", enabled_skills=["export_csv"])

    mock_redis.setex.assert_awaited_once()
    mock_redis.set.assert_not_awaited()

"""
Per-user persisted agent configuration in Redis.
"""

from __future__ import annotations

import json
from typing import Any

from src.cache.redis_client import get_redis
from src.config.settings import get_settings

_KEY_PREFIX = "user_agent_config:"


def _normalize_list(values: list[Any] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for v in values:
        s = str(v).strip()
        if s:
            out.append(s)
    return out


def _default_payload() -> dict[str, list[str]]:
    settings = get_settings()
    return {
        "enabled_skills": list(settings.enabled_skills or []),
        "skill_dirs": list(settings.skill_dirs or []),
        "mcp_servers": list(settings.mcp_servers or []),
    }


async def get_user_agent_config(user_sub: str) -> dict[str, list[str]]:
    client = await get_redis()
    raw = await client.get(f"{_KEY_PREFIX}{user_sub}")
    if not raw:
        return _default_payload()
    try:
        obj = json.loads(raw)
    except Exception:
        return _default_payload()
    return {
        "enabled_skills": _normalize_list(obj.get("enabled_skills")),
        "skill_dirs": _normalize_list(obj.get("skill_dirs")),
        "mcp_servers": _normalize_list(obj.get("mcp_servers")),
    }


async def set_user_agent_config(
    user_sub: str,
    *,
    enabled_skills: list[str] | None = None,
    skill_dirs: list[str] | None = None,
    mcp_servers: list[str] | None = None,
) -> dict[str, list[str]]:
    client = await get_redis()
    current = await get_user_agent_config(user_sub)
    if enabled_skills is not None:
        current["enabled_skills"] = _normalize_list(enabled_skills)
    if skill_dirs is not None:
        current["skill_dirs"] = _normalize_list(skill_dirs)
    if mcp_servers is not None:
        current["mcp_servers"] = _normalize_list(mcp_servers)

    settings = get_settings()
    await client.setex(
        f"{_KEY_PREFIX}{user_sub}",
        settings.redis_ttl_seconds,
        json.dumps(current),
    )
    return current

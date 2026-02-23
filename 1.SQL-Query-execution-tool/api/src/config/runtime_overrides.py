"""
Runtime overrides for agent config (skills/MCP) set via API.

These overrides are process-local and merged on top of .env settings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock
from typing import Any


@dataclass
class AgentRuntimeOverrides:
    enabled_skills: list[str] = field(default_factory=list)
    skill_dirs: list[str] = field(default_factory=list)
    mcp_servers: list[str] = field(default_factory=list)


_LOCK = Lock()
_OVERRIDES = AgentRuntimeOverrides()


def _normalize_list(values: list[Any] | None) -> list[str]:
    if not values:
        return []
    out: list[str] = []
    for v in values:
        s = str(v).strip()
        if s:
            out.append(s)
    return out


def get_agent_runtime_config(base_settings: Any) -> AgentRuntimeOverrides:
    """Return merged config from base settings and runtime overrides."""
    with _LOCK:
        enabled_skills = _OVERRIDES.enabled_skills or list(getattr(base_settings, "enabled_skills", []) or [])
        skill_dirs = _OVERRIDES.skill_dirs or list(getattr(base_settings, "skill_dirs", []) or [])
        mcp_servers = _OVERRIDES.mcp_servers or list(getattr(base_settings, "mcp_servers", []) or [])
        return AgentRuntimeOverrides(
            enabled_skills=_normalize_list(enabled_skills),
            skill_dirs=_normalize_list(skill_dirs),
            mcp_servers=_normalize_list(mcp_servers),
        )


def set_agent_runtime_config(
    *,
    enabled_skills: list[str] | None = None,
    skill_dirs: list[str] | None = None,
    mcp_servers: list[str] | None = None,
) -> AgentRuntimeOverrides:
    """Set runtime overrides and return current snapshot."""
    with _LOCK:
        if enabled_skills is not None:
            _OVERRIDES.enabled_skills = _normalize_list(enabled_skills)
        if skill_dirs is not None:
            _OVERRIDES.skill_dirs = _normalize_list(skill_dirs)
        if mcp_servers is not None:
            _OVERRIDES.mcp_servers = _normalize_list(mcp_servers)
        return AgentRuntimeOverrides(
            enabled_skills=list(_OVERRIDES.enabled_skills),
            skill_dirs=list(_OVERRIDES.skill_dirs),
            mcp_servers=list(_OVERRIDES.mcp_servers),
        )

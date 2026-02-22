"""
Skill registry: register skills (id, name, description, tools, target) and resolve by id or target.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

# Type for a single tool: callable (sync or async) that the agent can invoke.
ToolLike = Callable[..., Any]


class SkillTarget(str, Enum):
    """Which agent layer the skill's tools are attached to."""
    SUPERVISOR = "supervisor"
    SQL_EXECUTOR = "sql_executor"


@dataclass
class Skill:
    """A skill: id, display name, description, list of tools, and target agent."""
    id: str
    name: str
    description: str
    tools: list[ToolLike]
    target: SkillTarget


_registry: dict[str, Skill] = {}


def register_skill(skill: Skill) -> None:
    """Register a skill by id. Overwrites if id already exists."""
    _registry[skill.id] = skill


def resolve_skill(skill_id: str) -> Skill | None:
    """Return the skill for the given id, or None if not registered."""
    return _registry.get(skill_id)


def get_tools_for_target(enabled_skill_ids: list[str], target: SkillTarget) -> list[ToolLike]:
    """Return all tools from skills that are in enabled_skill_ids and have the given target."""
    out: list[ToolLike] = []
    for sid in enabled_skill_ids:
        skill = _registry.get(sid)
        if skill and skill.target == target:
            out.extend(skill.tools)
    return out


def clear_registry() -> None:
    """Clear all registered skills. Intended for tests."""
    _registry.clear()

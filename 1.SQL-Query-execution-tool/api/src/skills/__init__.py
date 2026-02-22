"""Skills package: registry and built-in skills for the agent."""

from src.skills.registry import (
    Skill,
    SkillTarget,
    register_skill,
    resolve_skill,
    get_tools_for_target,
    clear_registry,
)

__all__ = [
    "Skill",
    "SkillTarget",
    "register_skill",
    "resolve_skill",
    "get_tools_for_target",
    "clear_registry",
]

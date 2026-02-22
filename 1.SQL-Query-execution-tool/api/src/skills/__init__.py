"""Skills package: registry and built-in skills for the agent."""

from src.skills.registry import (
    Skill,
    SkillTarget,
    register_skill,
    resolve_skill,
    get_tools_for_target,
    clear_registry,
)
from src.skills.export_csv import register_export_csv_skill

# Register built-in skills so they are available when enabled via config.
register_export_csv_skill()

__all__ = [
    "Skill",
    "SkillTarget",
    "register_skill",
    "resolve_skill",
    "get_tools_for_target",
    "clear_registry",
]

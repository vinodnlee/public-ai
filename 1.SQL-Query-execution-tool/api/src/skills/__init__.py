"""Skills package: registry, built-in skills, and SKILL.md loader for the agent."""

from src.skills.registry import (
    Skill,
    SkillTarget,
    register_skill,
    resolve_skill,
    list_registered_skills,
    get_tools_for_target,
    clear_registry,
)
from src.skills.export_csv import register_export_csv_skill
from src.skills.skill_loader import SkillDoc, load_skills_from_dirs

# Register built-in skills so they are available when enabled via config.
register_export_csv_skill()

__all__ = [
    "Skill",
    "SkillTarget",
    "register_skill",
    "resolve_skill",
    "list_registered_skills",
    "get_tools_for_target",
    "clear_registry",
    "SkillDoc",
    "load_skills_from_dirs",
]

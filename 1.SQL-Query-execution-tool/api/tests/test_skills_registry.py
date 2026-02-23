"""
Tests for skills registry — register, resolve, get_tools_for_target.
"""

import pytest

from src.skills.registry import Skill, SkillTarget, register_skill, resolve_skill, get_tools_for_target, clear_registry


@pytest.fixture(autouse=True)
def _reset_registry() -> None:
    """Reset the global registry before each test so tests are isolated."""
    clear_registry()
    yield
    clear_registry()


def test_register_and_resolve_returns_skill() -> None:
    """Registering a skill and resolving by id should return the same skill."""
    def dummy_tool() -> str:
        return "ok"

    skill = Skill(
        id="export_csv",
        name="Export CSV",
        description="Export result as CSV",
        tools=[dummy_tool],
        target=SkillTarget.SUPERVISOR,
    )
    register_skill(skill)
    resolved = resolve_skill("export_csv")
    assert resolved is not None
    assert resolved.id == "export_csv"
    assert resolved.name == "Export CSV"
    assert resolved.target == SkillTarget.SUPERVISOR
    assert len(resolved.tools) == 1
    assert resolved.tools[0]() == "ok"


def test_resolve_unknown_id_returns_none() -> None:
    """Resolving an id that was never registered should return None."""
    assert resolve_skill("nonexistent") is None


def test_get_tools_for_target_returns_tools_of_matching_skills_only() -> None:
    """get_tools_for_target should return tools only from skills with matching target and id in enabled list."""
    def sup_tool() -> str:
        return "supervisor"
    def exec_tool() -> str:
        return "executor"

    register_skill(Skill(
        id="s1",
        name="S1",
        description="Supervisor skill",
        tools=[sup_tool],
        target=SkillTarget.SUPERVISOR,
    ))
    register_skill(Skill(
        id="e1",
        name="E1",
        description="Executor skill",
        tools=[exec_tool],
        target=SkillTarget.SQL_EXECUTOR,
    ))

    supervisor_tools = get_tools_for_target(["s1", "e1"], SkillTarget.SUPERVISOR)
    assert len(supervisor_tools) == 1
    assert supervisor_tools[0]() == "supervisor"

    executor_tools = get_tools_for_target(["s1", "e1"], SkillTarget.SQL_EXECUTOR)
    assert len(executor_tools) == 1
    assert executor_tools[0]() == "executor"


def test_get_tools_for_target_ignores_disabled_ids() -> None:
    """Only skills whose id is in enabled_ids should contribute tools."""
    def t() -> str:
        return "x"
    register_skill(Skill(
        id="s1",
        name="S1",
        description="",
        tools=[t],
        target=SkillTarget.SUPERVISOR,
    ))
    assert len(get_tools_for_target([], SkillTarget.SUPERVISOR)) == 0
    assert len(get_tools_for_target(["other"], SkillTarget.SUPERVISOR)) == 0
    assert len(get_tools_for_target(["s1"], SkillTarget.SUPERVISOR)) == 1

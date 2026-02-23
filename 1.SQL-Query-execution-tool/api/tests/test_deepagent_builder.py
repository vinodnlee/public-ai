"""
Tests for deepagent_builder: supervisor graph gets schema tool + enabled skill tools.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.agent.deepagent_builder import build_supervisor_graph
from src.skills.registry import SkillTarget, get_tools_for_target


@pytest.fixture
def mock_deps() -> tuple[MagicMock, MagicMock, list, MagicMock]:
    """Minimal mocks for adapter, semantic_layer, captured_events, checkpointer."""
    adapter = MagicMock()
    adapter.dialect = "postgresql"
    semantic_layer = MagicMock()
    captured_events: list = []
    checkpointer = MagicMock()
    return adapter, semantic_layer, captured_events, checkpointer


@patch("src.agent.deepagent_builder.get_llm")
def test_build_supervisor_graph_includes_schema_tool(
    m_llm: MagicMock, mock_deps: tuple
) -> None:
    """Without enabled skills, tools should contain at least the schema tool."""
    m_llm.return_value = MagicMock()
    adapter, semantic_layer, captured_events, checkpointer = mock_deps
    with patch("src.agent.deepagent_builder.get_settings") as m_get:
        m_get.return_value.enabled_skills = []
        with patch("src.agent.deepagent_builder.create_deep_agent") as m_create:
            m_create.return_value = MagicMock()
            build_supervisor_graph(adapter, semantic_layer, captured_events, checkpointer)
            m_create.assert_called_once()
            call_kw = m_create.call_args[1]
            tools = call_kw["tools"]
            assert len(tools) >= 1


@patch("src.agent.deepagent_builder.get_llm")
def test_build_supervisor_graph_includes_enabled_skill_tools(
    m_llm: MagicMock, mock_deps: tuple
) -> None:
    """With enabled_skills=['export_csv'], tools should include schema + export_csv tool."""
    m_llm.return_value = MagicMock()
    adapter, semantic_layer, captured_events, checkpointer = mock_deps
    skill_tools = get_tools_for_target(["export_csv"], SkillTarget.SUPERVISOR)
    assert len(skill_tools) >= 1, "export_csv skill should be registered and provide at least one tool"
    with patch("src.agent.deepagent_builder.get_settings") as m_get:
        m_get.return_value.enabled_skills = ["export_csv"]
        with patch("src.agent.deepagent_builder.create_deep_agent") as m_create:
            m_create.return_value = MagicMock()
            build_supervisor_graph(adapter, semantic_layer, captured_events, checkpointer)
            call_kw = m_create.call_args[1]
            tools = call_kw["tools"]
            assert len(tools) >= 2, "Should have get_schema_context plus at least one skill tool"


@patch("src.agent.deepagent_builder.get_llm")
def test_build_supervisor_graph_injects_skill_docs_into_prompt(
    m_llm: MagicMock, mock_deps: tuple
) -> None:
    """When skill_dirs are set and loader returns SkillDocs, system_prompt contains their content."""
    from src.skills.skill_loader import SkillDoc

    m_llm.return_value = MagicMock()
    adapter, semantic_layer, captured_events, checkpointer = mock_deps
    fake_doc = SkillDoc(
        path="/fake/path/SKILL.md",
        title="Test Skill",
        content="Use this skill to test prompt injection.",
    )
    with patch("src.agent.deepagent_builder.get_settings") as m_get:
        m_get.return_value.enabled_skills = []
        m_get.return_value.skill_dirs = ["/some/dir"]
        with patch("src.agent.deepagent_builder.load_skills_from_dirs", return_value=[fake_doc]):
            with patch("src.agent.deepagent_builder.create_deep_agent") as m_create:
                m_create.return_value = MagicMock()
                build_supervisor_graph(adapter, semantic_layer, captured_events, checkpointer)
                call_kw = m_create.call_args[1]
                prompt = call_kw["system_prompt"]
                assert "Use this skill to test prompt injection" in prompt
                assert "Test Skill" in prompt


@patch("src.agent.deepagent_builder.get_llm")
def test_build_supervisor_graph_includes_mcp_tools_when_returned(
    m_llm: MagicMock, mock_deps: tuple
) -> None:
    """When get_mcp_tools_for_supervisor returns tools, they are included in the graph."""
    m_llm.return_value = MagicMock()
    adapter, semantic_layer, captured_events, checkpointer = mock_deps
    mock_mcp_tool = MagicMock()
    mock_mcp_tool.name = "mcp_echo"
    with patch("src.agent.deepagent_builder.get_settings") as m_get:
        m_get.return_value.enabled_skills = []
        m_get.return_value.skill_dirs = []
        with patch("src.agent.deepagent_builder.get_mcp_tools_for_supervisor") as m_mcp:
            m_mcp.return_value = [mock_mcp_tool]
            with patch("src.agent.deepagent_builder.create_deep_agent") as m_create:
                m_create.return_value = MagicMock()
                build_supervisor_graph(adapter, semantic_layer, captured_events, checkpointer)
                call_kw = m_create.call_args[1]
                tools = call_kw["tools"]
                tool_names = [getattr(t, "name", None) for t in tools]
                assert "mcp_echo" in tool_names


@patch("src.agent.deepagent_builder.get_llm")
def test_build_supervisor_graph_adds_model_switch_middleware_when_enabled(
    m_llm: MagicMock, mock_deps: tuple
) -> None:
    m_llm.return_value = MagicMock()
    adapter, semantic_layer, captured_events, checkpointer = mock_deps
    with patch("src.agent.deepagent_builder.get_settings") as m_get:
        m_get.return_value.enabled_skills = []
        m_get.return_value.skill_dirs = []
        m_get.return_value.model_switch_enabled = True
        with patch("src.agent.deepagent_builder.get_mcp_tools_for_supervisor", return_value=[]):
            with patch("src.agent.deepagent_builder.build_dynamic_model_switch_middleware") as m_mw:
                m_mw.return_value = MagicMock()
                with patch("src.agent.deepagent_builder.create_deep_agent") as m_create:
                    m_create.return_value = MagicMock()
                    build_supervisor_graph(adapter, semantic_layer, captured_events, checkpointer)
                    call_kw = m_create.call_args[1]
                    assert "middleware" in call_kw
                    assert len(call_kw["middleware"]) == 1

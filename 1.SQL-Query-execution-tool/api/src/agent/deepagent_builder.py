"""Agent graph builder module."""

from deepagents import create_deep_agent  # type: ignore
from langgraph.checkpoint.memory import InMemorySaver  # type: ignore

from src.log import get_logger
from src.llm import get_llm
from src.config.settings import get_settings
from src.subagent.sql_executor.agent import build_config as sql_executor_config
from src.agent.events import AgentEvent
from src.db.adapters.base import DatabaseAdapter
from src.semantic.layer import SemanticLayer
from src.prompts.supervisor import SUPERVISOR_PROMPT_TEMPLATE
from src.tools.get_schema_context import get_schema_context_tool
from src.skills import get_tools_for_target, load_skills_from_dirs
from src.skills.registry import SkillTarget

logger = get_logger(__name__)


def _format_skills_section(skill_docs: list) -> str:
    """Format loaded SkillDocs into a markdown section for the system prompt."""
    if not skill_docs:
        return ""
    parts = ["\n## Loaded skills (SKILL.md)\n"]
    for doc in skill_docs:
        parts.append(f"\n### {doc.title}\n\n{doc.content}\n")
    return "".join(parts)


def build_supervisor_graph(
    adapter: DatabaseAdapter,
    semantic_layer: SemanticLayer,
    captured_events: list[AgentEvent],
    checkpointer: InMemorySaver,
):
    """Build and return the compiled supervisor agent graph."""
    model = get_llm()

    # Subagent for actually running SQL
    subagent = sql_executor_config(adapter, captured_events)

    # Closure that binds semantic_layer into the tool so the LLM only sees
    # a no-arg tool.  No @tool needed — create_deep_agent accepts Callable.
    async def get_schema_context() -> str:
        """Return the full semantic + physical schema context for the database."""
        return await get_schema_context_tool.coroutine(semantic_layer=semantic_layer)

    settings = get_settings()
    skill_docs = load_skills_from_dirs(settings.skill_dirs)
    skills_section = _format_skills_section(skill_docs)
    supervisor_prompt = SUPERVISOR_PROMPT_TEMPLATE.format(
        dialect=adapter.dialect,
        skills_section=skills_section,
    )

    skill_tools = get_tools_for_target(settings.enabled_skills, SkillTarget.SUPERVISOR)
    tools = [get_schema_context] + skill_tools

    logger.debug("Building supervisor graph with schema tool and %d skill tools", len(skill_tools))
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=supervisor_prompt,
        subagents=[subagent],
        checkpointer=checkpointer,
    )

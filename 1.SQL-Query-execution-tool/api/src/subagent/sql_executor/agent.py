"""SQL Executor subagent configuration builder."""

from src.log import get_logger
from src.tools.execute_sql import execute_sql
from src.db.adapters.base import DatabaseAdapter
from src.agent.events import AgentEvent
from src.prompts.sql_executor import SQL_EXECUTOR_PROMPT, SQL_EXECUTOR_DESCRIPTION

logger = get_logger(__name__)


def build_config(adapter: DatabaseAdapter, captured_events: list[AgentEvent]) -> dict:
    """Return a subagent config dict ready for create_deep_agent(subagents=[...])."""

    async def execute_sql_query(nl_query: str, sql: str) -> str:
        """Execute a read-only SELECT query and return results as JSON.

        Args:
            nl_query: The original natural language question from the user.
            sql: The SELECT SQL statement to execute.
        """
        return await execute_sql.coroutine(
            nl_query=nl_query,
            sql=sql,
            adapter=adapter,
            captured_events=captured_events,
        )

    logger.info("sql-executor subagent configured | dialect=%s",
                adapter.dialect)
    return {
        "name": "sql-executor",
        "description": SQL_EXECUTOR_DESCRIPTION,
        "system_prompt": SQL_EXECUTOR_PROMPT,
        "tools": [execute_sql_query],
    }

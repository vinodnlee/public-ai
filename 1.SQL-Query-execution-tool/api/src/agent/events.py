from enum import Enum
from typing import Any
from pydantic import BaseModel


class EventType(str, Enum):
    THINKING = "thinking"
    TOOL_CALL = "tool_call"
    SQL = "sql"
    EXECUTING = "executing"
    RESULT = "result"
    TOKEN = "token"
    ERROR = "error"
    DONE = "done"


class AgentEvent(BaseModel):
    type: EventType
    content: str | None = None
    tool: str | None = None
    input: str | None = None
    rows: list[dict[str, Any]] | None = None
    columns: list[str] | None = None
    row_count: int | None = None

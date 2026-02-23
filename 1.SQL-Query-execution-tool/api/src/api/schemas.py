from typing import Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=128)
    selected_skills: list[str] | None = None
    selected_skill_dirs: list[str] | None = None
    selected_mcp_servers: list[str] | None = None


class ChatInitResponse(BaseModel):
    session_id: str
    stream_url: str


class ApproveRequest(BaseModel):
    """Request to resume after HITL interrupt (approve/reject/edit SQL)."""

    thread_id: str = Field(..., min_length=1, max_length=64)
    session_id: str = Field(..., min_length=1, max_length=128)
    action: Literal["approve", "reject", "edit"] = Field(...)
    edited_sql: str | None = Field(None, min_length=1, max_length=10000)
    nl_query: str | None = Field(None, max_length=2000)
    selected_skills: list[str] | None = None
    selected_skill_dirs: list[str] | None = None
    selected_mcp_servers: list[str] | None = None


class ApproveInitResponse(BaseModel):
    """Response with new stream URL to consume continuation after approve."""

    stream_url: str


class SkillMeta(BaseModel):
    id: str
    name: str
    description: str
    target: str


class AgentConfigResponse(BaseModel):
    enabled_skills: list[str]
    skill_dirs: list[str]
    mcp_servers: list[str]
    available_skills: list[SkillMeta]


class AgentConfigUpdateRequest(BaseModel):
    enabled_skills: list[str] | None = None
    skill_dirs: list[str] | None = None
    mcp_servers: list[str] | None = None

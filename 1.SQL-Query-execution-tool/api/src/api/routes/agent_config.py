from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.api.schemas import (
    AgentConfigResponse,
    AgentConfigUpdateRequest,
    SkillMeta,
)
from src.auth.jwt import get_current_user
from src.config.user_agent_config import get_user_agent_config, set_user_agent_config
from src.skills import list_registered_skills

router = APIRouter(prefix="/agent-config", tags=["agent-config"])


async def _build_response(user_sub: str) -> AgentConfigResponse:
    runtime = await get_user_agent_config(user_sub)
    skills = [
        SkillMeta(
            id=s.id,
            name=s.name,
            description=s.description,
            target=s.target.value,
        )
        for s in list_registered_skills()
    ]
    return AgentConfigResponse(
        enabled_skills=runtime["enabled_skills"],
        skill_dirs=runtime["skill_dirs"],
        mcp_servers=runtime["mcp_servers"],
        available_skills=skills,
    )


@router.get("", response_model=AgentConfigResponse)
async def get_agent_config(_user: dict = Depends(get_current_user)) -> JSONResponse:
    user_sub = str(_user.get("sub", "anonymous"))
    return JSONResponse(content=(await _build_response(user_sub)).model_dump())


@router.put("", response_model=AgentConfigResponse)
async def update_agent_config(
    body: AgentConfigUpdateRequest,
    _user: dict = Depends(get_current_user),
) -> JSONResponse:
    user_sub = str(_user.get("sub", "anonymous"))
    await set_user_agent_config(
        user_sub,
        enabled_skills=body.enabled_skills,
        skill_dirs=body.skill_dirs,
        mcp_servers=body.mcp_servers,
    )
    return JSONResponse(content=(await _build_response(user_sub)).model_dump())

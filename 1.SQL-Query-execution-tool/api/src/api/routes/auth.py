"""Login and JWT issuance."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.log import get_logger
from src.auth.jwt import create_access_token, get_current_user
from src.config.settings import get_settings

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest) -> TokenResponse:
    if not settings.auth_enabled:
        logger.info("Auth disabled — issuing bypass token")
        return TokenResponse(access_token="disabled", token_type="bearer")
    if data.username != settings.admin_username or data.password != settings.admin_password:
        logger.warning("Login failed for user=%s", data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(sub=data.username)
    logger.info("Login success | user=%s", data.username)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me")
async def me(user: dict = Depends(get_current_user)) -> dict:
    return {"sub": user.get("sub", "anonymous")}

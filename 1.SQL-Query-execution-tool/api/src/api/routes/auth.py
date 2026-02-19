"""
Login and JWT issuance. Demo: single admin user from env.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.auth.jwt import create_access_token, get_current_user
from src.config.settings import get_settings

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
    """Issue JWT for valid admin credentials. No-op when auth is disabled."""
    if not settings.auth_enabled:
        return TokenResponse(access_token="disabled", token_type="bearer")
    if data.username != settings.admin_username or data.password != settings.admin_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(sub=data.username)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me")
async def me(user: dict = Depends(get_current_user)) -> dict:
    """Return current user from JWT (for UI to check auth)."""
    return {"sub": user.get("sub", "anonymous")}

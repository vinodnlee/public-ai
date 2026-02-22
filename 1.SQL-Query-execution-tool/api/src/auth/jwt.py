"""JWT creation and verification."""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.log import get_logger
from src.config.settings import get_settings

logger = get_logger(__name__)
settings = get_settings()
_scheme = HTTPBearer(auto_error=False)


def create_access_token(sub: str, extra: dict[str, Any] | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": sub, "exp": expire, "iat": datetime.now(timezone.utc)}
    if extra:
        payload.update(extra)
    logger.debug("Token created for sub=%s", sub)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        logger.debug("Token verified for sub=%s", payload.get("sub"))
        return payload
    except jwt.PyJWTError:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_token_from_request(request: Request) -> str | None:
    auth: HTTPAuthorizationCredentials | None = await _scheme(request)
    if auth:
        return auth.credentials
    return request.query_params.get("token")


async def get_current_user(request: Request) -> dict[str, Any]:
    if not settings.auth_enabled:
        return {"sub": "anonymous"}
    token = await get_token_from_request(request)
    if not token:
        logger.warning("Unauthenticated request to %s", request.url.path)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return verify_token(token)

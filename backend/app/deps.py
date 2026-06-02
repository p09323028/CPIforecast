from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings

_bearer = HTTPBearer(auto_error=True)


def verify_admin_token(
    creds: HTTPAuthorizationCredentials = Depends(_bearer),
) -> None:
    if not settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="server has no ADMIN_TOKEN configured",
        )
    if creds.credentials != settings.ADMIN_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid admin token",
        )

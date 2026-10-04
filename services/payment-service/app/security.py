from fastapi import Header, HTTPException, status

from app.config import settings


def verify_service_token(
    x_service_token: str | None = Header(default=None),
):
    if not x_service_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing service authentication",
        )

    if x_service_token != settings.service_auth_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid service authentication",
        )

    return True
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import RefreshToken

def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token(
    db: Session,
    user_id : uuid.UUID,
) -> str:

    raw_token = secrets.token_urlsafe(64)

    token_hash = hash_refresh_token(raw_token)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=settings.refresh_token_expire_days)
    )

    refresh_token = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at
    )

    db.add(refresh_token)
    db.commit()

    return raw_token

def get_valid_refresh_token(
    db: Session,
    raw_token: str,
) -> RefreshToken:
    token_hash = hash_refresh_token(raw_token)

    refresh_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    if not refresh_token:
        raise ValueError("Invalid refresh token")

    if refresh_token.revoked_at is not None:
        raise ValueError("Invalid refresh token")

    if refresh_token.expires_at <= datetime.now(timezone.utc):
        raise ValueError("Invalid refresh token")

    return refresh_token

def rotate_refresh_token(
    db: Session,
    raw_token: str,
) -> tuple[RefreshToken, str]:
    stored_token = get_valid_refresh_token(
        db=db,
        raw_token=raw_token,
    )

    stored_token.revoked_at = datetime.now(timezone.utc)

    new_raw_token = secrets.token_urlsafe(64)

    new_token_hash = hash_refresh_token(new_raw_token)

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )

    new_refresh_token = RefreshToken(
        user_id=stored_token.user_id,
        token_hash=new_token_hash,
        expires_at=expires_at,
    )

    db.add(new_refresh_token)

    try:
        db.commit()
        db.refresh(new_refresh_token)
    except Exception:
        db.rollback()
        raise

    return new_refresh_token, new_raw_token


def revoke_refresh_token(
    db: Session,
    raw_token: str,
) -> None:
    token_hash = hash_refresh_token(raw_token)

    refresh_token = db.scalar(
        select(RefreshToken).where(
            RefreshToken.token_hash == token_hash
        )
    )

    if not refresh_token:
        raise ValueError("Invalid refresh token")

    if refresh_token.revoked_at is not None:
        raise ValueError("Invalid refresh token")

    refresh_token.revoked_at = datetime.now(timezone.utc)

    db.commit()
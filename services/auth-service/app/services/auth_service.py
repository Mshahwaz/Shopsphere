from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthUser
from app.security import hash_password,verify_password,create_access_token

from app.clients.user_client import create_user_profile
import logging

logger=logging.getLogger(__name__)

def register_user(
    db: Session,
    email: str,
    password: str
    ) -> AuthUser:

    existing_user= db.scalar(
        select(AuthUser).where(AuthUser.email == email)
    )

    if existing_user:
        raise ValueError("Email Already registered")

    user=AuthUser(
        email=email,
        password_hash=hash_password(password),
        role="USER",
        is_active=True,
    )
    try:
        db.add(user)
        db.commit()
        db.refresh(user)

        create_user_profile(str(user.id))

    except Exception:
        db.rollback()

        try:
            delete_user(db=db,user=user)
        except Exception:
            db.rollback()
            logger.exception(
            "Failed to compensate AuthUser %s after User profile creation failed",
            user.id,
            )
        raise
    
    return user

def delete_user(
    db: Session,
    user: AuthUser
) -> None:
    db.delete(user)
    db.commit()

def authenticate_user(
    db: Session,
    email: str,
    password: str
) -> str:

    user = db.scalar(
        select(AuthUser).where(
            AuthUser.email == email
        )
    )

    if not user:
        raise ValueError("Invalid email and password")

    if not user.is_active:
        raise ValueError("Invalid email and password")

    if not verify_password(password,user.password_hash):
        raise ValueError("Invalid email and password")

    return create_access_token(
        user_id=str(user.id),
        role=user.role
    )

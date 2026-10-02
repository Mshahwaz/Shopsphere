from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthUser
from app.security import hash_password,verify_password,create_access_token


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
    except Exception:
        db.rollback()
        raise
    
    return user

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

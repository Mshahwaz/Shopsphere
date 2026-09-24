from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthUser
from app.security import hash_password


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
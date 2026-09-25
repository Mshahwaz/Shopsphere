import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User

def get_user_by_auth_id(
    db: Session,
    auth_user_id: uuid.UUID
) -> User | None:
    return db.scalar(
        select(User).where(
            User.auth_user_id == auth_user_id
        )
    )
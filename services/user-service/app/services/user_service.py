import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import User
from app.schemas import UserUpdateRequest



def get_user_by_auth_id(
    db: Session,
    auth_user_id: uuid.UUID
) -> User | None:
    return db.scalar(
        select(User).where(
            User.auth_user_id == auth_user_id
        )
    )

def update_user(
    db: Session,
    auth_user_id: uuid.UUID,
    request: UserUpdateRequest
) -> User | None:
    
    user=get_user_by_auth_id(db,auth_user_id)

    if user is None:
        return None

    if request.first_name is not None:
        user.first_name = request.first_name
    
    if request.last_name is not None:
        user.last_name = request.last_name
    
    if request.phone is not None:
        user.phone = request.phone

    db.commit()
    db.refresh(user)

    return user

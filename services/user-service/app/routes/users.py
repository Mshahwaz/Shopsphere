import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserResponse,UserUpdateRequest
from app.services.user_service import get_user_by_auth_id, update_user
from app.security import get_current_user 

router=APIRouter(
    prefix="/api/v1/users",
    tags=["Users"],
)

@router.get("/me",response_model=UserResponse)
def get_my_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):

    auth_user_id = uuid.UUID(current_user["user_id"])
    user = get_user_by_auth_id(
        db,
        auth_user_id
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Profile not found"
        )
    return user

@router.patch("/me", response_model=UserResponse)
def update_my_profile(
    request: UserUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    auth_user_id = uuid.UUID(current_user["user_id"])

    user = update_user(
        db,
        auth_user_id,
        request=request,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found",
        )

    return user
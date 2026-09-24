from fastapi import HTTPException, APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserRegisterRequest, UserResponse
from app.services.auth_service import register_user


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    )
def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db),
    ):
    try:
        user=register_user(
            db,
            email=request.email,
            password=request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc)
        )
    return user
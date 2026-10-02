from fastapi import HTTPException, APIRouter, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    UserRegisterRequest,
    UserResponse,
    UserLoginRequest,
    TokenResponse
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
)
from app.security import get_current_user

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

@router.post("/login", response_model=TokenResponse)
def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db),
):
    try:
        access_token = authenticate_user(
            db,
            request.email,
            request.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.get("/me")
def get_authenticated_user(
    current_user: dict = Depends(get_current_user),
):
    return current_user
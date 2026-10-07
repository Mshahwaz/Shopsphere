from fastapi import (
    HTTPException,
    APIRouter,
    status,
    Depends, 
    Response,
    Cookie
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuthUser
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
from app.services.refresh_token_service import (
    create_refresh_token,
    get_valid_refresh_token,
    rotate_refresh_token,
    revoke_refresh_token
)
from app.security import (
    get_current_user, 
    require_role,
    create_access_token
)
from app.clients.user_client import UserProfileCreationException
from app.config import settings

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
    except UserProfileCreationException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to complete registration because the user profile service is unavailable"
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
    response: Response,
    db: Session = Depends(get_db),
):
    try:
        user = authenticate_user(
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

    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role,
    )

    refresh_token = create_refresh_token(
        db=db,
        user_id=user.id,
    )

    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=refresh_token,
        httponly=settings.refresh_token_cookie_httponly,
        secure=settings.refresh_token_cookie_secure,
        samesite=settings.refresh_token_cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
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


@router.get("/admin-test")
def admin_test(
    current_user: dict = Depends(require_role("ADMIN")),
):

    return {
        "message": "Admin Access granted",
        "user": current_user
    }


@router.post(
    "/refresh",
    response_model=TokenResponse,
)
def refresh_access_token(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        stored_token, new_raw_token = rotate_refresh_token(
            db=db,
            raw_token=refresh_token,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.scalar(
        select(AuthUser).where(
            AuthUser.id == stored_token.user_id
        )
    )

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(
        user_id=str(user.id),
        role=user.role,
    )

    response.set_cookie(
        key=settings.refresh_token_cookie_name,
        value=new_raw_token,
        httponly=settings.refresh_token_cookie_httponly,
        secure=settings.refresh_token_cookie_secure,
        samesite=settings.refresh_token_cookie_samesite,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
    )

@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    try:
        revoke_refresh_token(
            db=db,
            raw_token=refresh_token,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    response.delete_cookie(
        key=settings.refresh_token_cookie_name,
        path="/api/v1/auth",
    )

    return {"message": "Logged out successfully"}
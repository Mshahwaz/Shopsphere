import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.schemas import (
    CategoryCreateRequest,
    CategoryResponse
)
from app.services.product_service import (
    create_category,
    get_categories,
    get_category_by_id
)

from app.security import require_role

router=APIRouter(
    prefix="/api/v1/categories",
    tags=["Categories"]
)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
    )
def create_category_endpoint(
    request: CategoryCreateRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role("ADMIN")),
    ):

    try:
        return create_category(
            db=db,
            name=request.name
        )
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )

@router.get(
    "",
    response_model=list[CategoryResponse],
    )
def list_categories(
    db: Session = Depends(get_db)
):
    return get_categories(db=db)

@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_category_endpoint(
    category_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    category=get_category_by_id(db=db,category_id=category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category
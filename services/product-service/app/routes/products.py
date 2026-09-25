import uuid

from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    ProductCreateRequest,
    ProductResponse
)
from app.services.product_service import (
    create_product,
    get_product_by_id,
    get_products,
)


router=APIRouter(
    prefix="/api/v1/products",
    tags=["Products"]
)

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    request: ProductCreateRequest,
    db: Session = Depends(get_db)
    ):

    return create_product(
        db=db,
        request=request
    )

@router.get(
    "/{product_id}",
    response_model=ProductResponse
    )
def get_product_by_id_endpoint(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
    ):

    product=get_product_by_id(
        db=db,
        product_id=product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product

@router.get("",response_model=list[ProductResponse])
def list_products(
    active_only: bool = True,
    category_id: uuid.UUID | None = None,
    db: Session = Depends(get_db)   
    ):
    return get_products(
        db=db,
        active_only=active_only,
        category_id=category_id
        )
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CartItemCreateRequest,
    CartItemResponse,
    CartResponse
)
from app.services.cart_service import add_item_to_cart, get_cart


router = APIRouter(
    prefix="/api/v1/cart",
    tags=["Cart"],
)

@router.post(
    "/items",
    response_model=CartItemResponse,
)
def add_cart_item(
    request: CartItemCreateRequest,
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return add_item_to_cart(
        db=db,
        user_id=user_id,
        product_id=request.product_id,
        quantity=request.quantity,
    )

@router.get("",response_model=CartResponse)
def get_cart_endpoint(
    user_id: uuid.UUID,
    db:Session = Depends(get_db)
    ):
    result = get_cart(
        db=db,
        user_id=user_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    cart, items = result

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items
    )
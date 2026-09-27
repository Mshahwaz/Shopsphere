import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CartItemCreateRequest,
    CartItemResponse,
    CartResponse,
    CartItemUpdateRequest,
)
from app.services.cart_service import (
    add_item_to_cart,
    get_cart,
    update_cart_item_quantity,
    remove_cart_item,
    clear_cart
    )


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

@router.patch(
    "/items/{product_id}",
    response_model=CartItemResponse,
)
def update_cart_item_quantity_endpoint(
    product_id: uuid.UUID,
    user_id: uuid.UUID,
    request: CartItemUpdateRequest,
    db: Session = Depends(get_db)
):
    cart_item=update_cart_item_quantity(
        db=db,
        user_id=user_id,
        product_id=product_id,
        quantity=request.quantity,
    )

    if cart_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found",
        )

    return cart_item

@router.delete(
    "/items/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_cart_item_endpoint(
    product_id: uuid.UUID,
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    removed=remove_cart_item(
        db=db,
        user_id=user_id,
        product_id=product_id
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart Item not found"
        )

@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT
)
def clear_cart_endpoint(
    user_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    cleared = clear_cart(
        db=db,
        user_id=user_id
    )

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart Not Found"
        )
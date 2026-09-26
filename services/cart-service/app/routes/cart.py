import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CartItemCreateRequest,
    CartItemResponse,
)
from app.services.cart_service import add_item_to_cart


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
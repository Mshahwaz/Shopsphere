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

from app.security import get_current_user
from app.clients.exceptions import (
    ProductNotFoundError,
    ProductServiceError,
    ProductServiceTimeoutError,
    ProductServiceUnavailableError
)
from app.security import get_current_user, verify_service_token

router = APIRouter(
    prefix="/api/v1/cart",
    tags=["Cart"],
)

internal_router = APIRouter(
    prefix="/api/v1/internal",
    tags=["Internal"],
)

@router.post(
    "/items",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED
)
def add_cart_item(
    request: CartItemCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    try:
        return add_item_to_cart(
            db=db,
            user_id=user_id,
            product_id=request.product_id,
            quantity=request.quantity,
        )
    except ProductNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except ProductServiceTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Product Service timed out",
        )

    except ProductServiceUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Product Service is unavailable",
        )

    except ProductServiceError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Product Service returned an error",
        )

@router.get("", response_model=CartResponse)
def get_cart_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    result = get_cart(
        db=db,
        user_id=user_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )

    cart, items = result

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items,
    )

@router.patch(
    "/items/{product_id}",
    response_model=CartItemResponse,
)
def update_cart_item_quantity_endpoint(
    product_id: uuid.UUID,
    request: CartItemUpdateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    cart_item = update_cart_item_quantity(
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
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_cart_item_endpoint(
    product_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    removed = remove_cart_item(
        db=db,
        user_id=user_id,
        product_id=product_id,
    )

    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart Item not found",
        )

@router.delete(
    "",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_cart_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    cleared = clear_cart(
        db=db,
        user_id=user_id,
    )

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart Not Found",
        )

@internal_router.get(
    "/cart/{user_id}",
    response_model=CartResponse,
)
def get_internal_cart(
    user_id: uuid.UUID,
    _: None = Depends(verify_service_token),
    db: Session = Depends(get_db),
):
    result = get_cart(
        db=db,
        user_id=user_id,
    )

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Cart not found",
        )

    cart, items = result

    return CartResponse(
        id=cart.id,
        user_id=cart.user_id,
        items=items,
    )

@internal_router.delete(
    "/cart/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def clear_internal_cart(
    user_id: uuid.UUID,
    _: None = Depends(verify_service_token),
    db: Session = Depends(get_db),
):
    cleared = clear_cart(
        db=db,
        user_id=user_id,
    )

    if not cleared:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found",
        )
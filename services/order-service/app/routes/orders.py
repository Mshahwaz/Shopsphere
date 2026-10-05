import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    OrderSummaryResponse,
)

from app.services.order_service import (
    create_order,
    get_order_for_user,
    get_order_items,
    get_order_by_user,
)

from app.clients.exceptions import (
    ProductNotFoundError,
    ProductServiceError,
    ProductServiceTimeoutError,
    ProductServiceUnavailableError,
    InsufficientStockError,
    InventoryNotFoundError,
    InventoryServiceError,
    InventoryServiceTimeoutError,
    InventoryServiceUnavailableError,
    PaymentFailedError,
    PaymentNotFoundError,
    PaymentServiceTimeoutError,
    PaymentServiceUnavailableError,
    PaymentServiceError,
)

from app.security import get_current_user


router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)


# ---------------------------------------------------------
# Create Order
# ---------------------------------------------------------

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    request: OrderCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    try:
        order = create_order(
            db=db,
            request=request,
            user_id=user_id,
        )

    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ProductServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except ProductServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except ProductServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except InventoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except InventoryServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except InventoryServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except InventoryServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except PaymentFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exc),
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except PaymentServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except PaymentServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except PaymentServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    items = [
        OrderItemResponse.model_validate(item)
        for item in order_items_for_response(
            db=db,
            order_id=order.id,
        )
    ]

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        items=items,
    )


# ---------------------------------------------------------
# Helper: Order Items
# ---------------------------------------------------------

def order_items_for_response(
    db: Session,
    order_id,
):
    from sqlalchemy import select
    from app.models import OrderItem

    return db.scalars(
        select(OrderItem)
        .where(
            OrderItem.order_id == order_id
        )
        .order_by(OrderItem.created_at)
    ).all()


# ---------------------------------------------------------
# Get Single Order
# ---------------------------------------------------------

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order_endpoint(
    order_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    order = get_order_for_user(
        db=db,
        order_id=order_id,
        user_id=user_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    items = get_order_items(
        db=db,
        order_id=order.id,
    )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        items=[
            OrderItemResponse.model_validate(item)
            for item in items
        ],
    )


# ---------------------------------------------------------
# List Current User's Orders
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[OrderSummaryResponse],
)
def list_orders_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    return get_order_by_user(
        db=db,
        user_id=user_id,
    )



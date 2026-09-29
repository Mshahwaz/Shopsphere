import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    OrderSummaryResponse,
    OrderStatusUpdateRequest
)
from app.services.order_service import (
    create_order,
    get_order,
    get_order_items,
    get_order_by_user,
    update_order_status
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
    InventoryServiceUnavailableError
)

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)

## ------ Create Order Endpoint
@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
):
    try:
        order = create_order(
            db=db,
            request=request,
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
            status_code=404,
            detail=str(exc),
        )

    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        )

    except InventoryServiceTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=str(exc),
        )

    except InventoryServiceUnavailableError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc),
        )

    except InventoryServiceError as exc:
        raise HTTPException(
            status_code=502,
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

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order_endpoint(
    order_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    order = get_order(
        db=db,
        order_id=order_id,
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

@router.get(
    "",
    response_model=list[OrderSummaryResponse],
)
def list_orders_endpoint(
    user_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    return get_order_by_user(
        db=db,
        user_id=user_id,
    )

@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
)
def update_order_status_endpoint(
    order_id: uuid.UUID,
    request: OrderStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        order = update_order_status(
            db=db,
            order_id=order_id,
            new_status=request.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
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
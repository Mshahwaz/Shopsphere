import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
    OrderSummaryResponse
)
from app.services.order_service import (
    create_order,
    get_order,
    get_order_items,
    get_order_by_user
    )

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)

@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    request: OrderCreateRequest,
    db: Session = Depends(get_db),
):
    order = create_order(
        db=db,
        request=request,
    )

    # Retrieve the items belonging to this order.
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
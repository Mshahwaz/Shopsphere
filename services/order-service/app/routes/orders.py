from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    OrderCreateRequest,
    OrderItemResponse,
    OrderResponse,
)
from app.services.order_service import create_order

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
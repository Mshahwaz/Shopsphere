import uuid
from decimal import Decimal
from sqlalchemy import select

from sqlalchemy.orm import Session

from app.schemas import (
    OrderCreateRequest,
)
from app.models import Order, OrderItem
from app.clients.product_client import get_product

def create_order(
    db: Session,
    request: OrderCreateRequest
) -> Order:
    
    total_amount = Decimal("0.00")

    order = Order(
        user_id= request.user_id,
        status="PENDING",
        total_amount=Decimal("0.00"),
    )
    try:
        db.add(order)
        db.flush()

        order_items = []

        for item in request.items:

            # Get authoritative product information
            product = get_product(item.product_id)

            product_name = product["name"]
            unit_price = Decimal(str(product["price"]))

            item_total = unit_price * item.quantity

            total_amount += item_total

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=product_name,
                unit_price=unit_price,
                quantity=item.quantity,
            )

            db.add(order_item)
            order_items.append(order_item)

        order.total_amount = total_amount

        db.commit()
        db.refresh(order)

        for order_item in order_items:
            db.refresh(order_item)

        return order

    except Exception:
        db.rollback()
        raise

def get_order(
    db: Session,
    order_id: uuid.UUID,
) -> Order | None:
    return db.scalar(
        select(Order).where(
            Order.id == order_id
        )
    )

def get_order_items(
    db: Session,
    order_id: uuid.UUID
) -> list[OrderItem]:
    return list(
        db.scalars(
            select(OrderItem)
            .where(
                OrderItem.order_id == order_id
            )
            .order_by(OrderItem.created_at)
        ).all()
    )

def get_order_by_user(
    db: Session,
    user_id: uuid.UUID
) -> list[Order]:
    return list(
        db.scalars(
            select(Order).where(
                Order.user_id == user_id
            )
            .order_by(
                Order.created_at.desc()
            )
        ).all()
    )


VALID_ORDER_STATUSES = {
    "PENDING",
    "CONFIRMED",
    "PAYMENT_FAILED",
    "CANCELLED",
}

ALLOWED_STATUS_TRANSITIONS = {
    "PENDING": {
        "CONFIRMED",
        "PAYMENT_FAILED",
        "CANCELLED",
    },
    "CONFIRMED": set(),
    "PAYMENT_FAILED": set(),
    "CANCELLED": set(),
}


def update_order_status(
    db: Session,
    order_id: uuid.UUID,
    new_status: str,
) -> Order | None:

    if new_status not in VALID_ORDER_STATUSES:
        raise ValueError(
            "Invalid order status"
        )

    order = db.scalar(
        select(Order).where(
            Order.id == order_id
        )
    )

    if order is None:
        return None

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(
        order.status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Cannot change order status "
            f"from {order.status} to {new_status}"
        )

    order.status = new_status

    try:
        db.commit()
        db.refresh(order)
    except Exception:
        db.rollback()
        raise

    return order
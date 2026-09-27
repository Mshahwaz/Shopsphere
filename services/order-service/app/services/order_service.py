from decimal import Decimal

from sqlalchemy.orm import Session

from app.schemas import (
    OrderCreateRequest,
)
from app.models import Order, OrderItem

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

            item_total = (
                item.unit_price * item.quantity
            )

            total_amount += item_total

            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
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
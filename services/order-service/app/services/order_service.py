import uuid
from decimal import Decimal
from sqlalchemy import select, and_

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models import Order, OrderItem, OutboxEvent
from app.clients.product_client import get_product
from app.clients.inventory_client import (
    reserve_stock,
    release_stock,
    reduce_stock
)
from app.clients.payment_client import create_checkout
from app.clients.exceptions import PaymentFailedError

from app.clients.cart_client import (
    get_cart,
    clear_cart,
)
from app.clients.exceptions import (
    EmptyCartError
)


def create_order(
    db: Session,
    user_id: uuid.UUID,
) -> tuple[Order, dict]:

    # =========================================================
    # 1. Get user's cart
    # =========================================================

    cart = get_cart(
        user_id=user_id,
    )

    cart_items = cart.get("items", [])

    if not cart_items:
        raise EmptyCartError(
            "Cart is empty"
        )

    total_amount = Decimal("0.00")

    order = Order(
        user_id= user_id,
        status="PENDING",
        total_amount=Decimal("0.00"),
    )

    try:
        db.add(order)
        db.flush()

        order_items = []

        # =====================================================
        # 2. Process every Cart item
        # =====================================================

        for cart_item in cart_items:

            product_id = uuid.UUID(
                str(cart_item["product_id"])
            )

            quantity = cart_item["quantity"]

            # -------------------------------------------------
            # Product Service
            # -------------------------------------------------

            product = get_product(
                product_id
            )

            product_name = product["name"]

            unit_price = Decimal(
                str(product["price"])
            )

            # -------------------------------------------------
            # Inventory Service
            # -------------------------------------------------

            reserve_stock(
                product_id=product_id,
                quantity=quantity,
            )

            # -------------------------------------------------
            # Calculate total
            # -------------------------------------------------

            item_total = (
                unit_price * quantity
            )

            total_amount += item_total

            # -------------------------------------------------
            # Create OrderItem snapshot
            # -------------------------------------------------

            order_item = OrderItem(
                order_id=order.id,
                product_id=product_id,
                product_name=product_name,
                unit_price=unit_price,
                quantity=quantity,
            )

            db.add(order_item)

            order_items.append(
                order_item
            )

        # =====================================================
        # 3. Persist pending order
        # =====================================================

        order.total_amount = total_amount

        db.commit()

        db.refresh(order)

        for order_item in order_items:
            db.refresh(order_item)

    except Exception:
        db.rollback()
        raise

    # =========================================================
    # 4. Create Razorpay Checkout
    # =========================================================

    try:
        checkout = create_checkout(
            order_id=order.id,
            amount=order.total_amount,
        )

    except Exception:
        # Checkout creation failed or its outcome is uncertain.
        # Keep the order PENDING rather than falsely confirming
        # or marking payment as failed.
        #
        # Inventory compensation requires more careful handling
        # because a timeout does not prove Razorpay created
        # nothing. We will harden this in a later step.
        raise

    return order, checkout


def get_order(
    db: Session,
    order_id: uuid.UUID,
) -> Order | None:
    return db.scalar(
        select(Order).where(
            Order.id == order_id
        )
    )
def get_order_for_user(
    db: Session,
    order_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Order | None:
    return db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
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
    user_id: uuid.UUID,
    new_status: str,
) -> Order | None:

    if new_status not in VALID_ORDER_STATUSES:
        raise ValueError(
            "Invalid order status"
        )

    order = db.scalar(
        select(Order).where(
            Order.id == order_id,
            Order.user_id == user_id,
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

def confirm_order_after_payment(
    db: Session,
    order_id: uuid.UUID,
    user_id: uuid.UUID,
    payment: dict,
) -> Order | None:
    """
    Confirm an order after the Payment Service has verified
    a successful payment.

    Inventory finalization is performed before the order
    confirmation transaction is committed.
    """

    # 1. Validate the result returned by the Payment Service.
    if payment.get("status") != "SUCCESS":
        raise ValueError(
            "Order can only be confirmed after successful payment"
        )

    payment_order_id = payment.get("order_id")

    if payment_order_id is None:
        raise ValueError(
            "Payment response does not contain an order ID"
        )

    if str(payment_order_id) != str(order_id):
        raise ValueError(
            "Payment does not belong to this order"
        )

    try:
        # 2. Lock the order row.
        order = db.scalar(
            select(Order)
            .where(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .with_for_update()
        )

        if order is None:
            return None

        # 3. Make repeated successful requests idempotent
        #    after the order has already been confirmed.
        if order.status == "CONFIRMED":
            return order

        # 4. Do not confirm orders in an invalid state.
        if order.status != "PENDING":
            raise ValueError(
                f"Cannot confirm order with status {order.status}"
            )

        # 5. Load the order's item snapshots.
        items = list(
            db.scalars(
                select(OrderItem).where(
                    OrderItem.order_id == order.id
                )
            ).all()
        )

        if not items:
            raise ValueError(
                "Cannot confirm an order without items"
            )

        # 6. Finalize the previously reserved inventory.
        #
        # IMPORTANT:
        # Inventory Service has a separate database.
        # These calls cannot be rolled back by db.rollback().
        for item in items:
            operation_id = uuid.uuid5(
                order.id,
                str(item.id),
            )

            reduce_stock(
                product_id=item.product_id,
                quantity=item.quantity,
                operation_id=operation_id,
            )

        # 7. Update the order and create its outbox event
        #    in the same Order Service database transaction.
        order.status = "CONFIRMED"

        existing_event = db.scalar(
            select(OutboxEvent).where(
                OutboxEvent.event_type == "order.confirmed",
                OutboxEvent.aggregate_type == "Order",
                OutboxEvent.aggregate_id == order.id,
            )
        )

        if existing_event is None:
            event_payload = {
                "order_id": str(order.id),
                "user_id": str(order.user_id),
                "status": "CONFIRMED",
                "total_amount": str(order.total_amount),
                "payment_id": str(payment.get("id", "")),
                "items": [
                    {
                        "product_id": str(item.product_id),
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "unit_price": str(item.unit_price),
                    }
                    for item in items
                ],
            }

            db.add(
                OutboxEvent(
                    event_type="order.confirmed",
                    aggregate_type="Order",
                    aggregate_id=order.id,
                    payload=event_payload,
                )
            )

        db.commit()
        db.refresh(order)

        return order

    except Exception:
        db.rollback()
        raise
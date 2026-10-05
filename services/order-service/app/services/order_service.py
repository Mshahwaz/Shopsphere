import uuid
from decimal import Decimal
from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models import Order, OrderItem
from app.clients.product_client import get_product
from app.clients.inventory_client import (
    reserve_stock,
    release_stock,
    reduce_stock
)
from app.clients.payment_client import (
    create_payment,
    process_payment,
)
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
) -> Order:

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

    # 5. Create payment
    payment = create_payment(
        order_id=order.id,
        amount=order.total_amount,
    )

    # 6. Process payment
    try:
        payment_result = process_payment(
            payment_id=payment["id"],
        )

    except PaymentFailedError:

        # Payment is known to have failed.
        # Release all inventory reservations.
        try:
            for order_item in order_items:
                release_stock(
                    product_id=order_item.product_id,
                    quantity=order_item.quantity,
                )

        except Exception:
            # Compensation failed.
            # Keep the order pending so that we do not falsely
            # claim that the inventory was successfully released.
            raise

        order.status = "PAYMENT_FAILED"

        db.commit()
        db.refresh(order)

        raise

    # 7. Confirm order
    if payment_result["status"] == "SUCCESS":

        # Payment succeeded, so finalize the inventory reservation.
        for order_item in order_items:
            reduce_stock(
                product_id=order_item.product_id,
                quantity=order_item.quantity,
            )

        order.status = "CONFIRMED"

        db.commit()
        db.refresh(order)

        # -----------------------------------------------------
        # Clear cart
        # -----------------------------------------------------
        #
        # Order is already confirmed at this point.
        #
        # If cart clearing fails, we MUST NOT change the
        # confirmed order back to failed.
        #
        # The cart may temporarily remain and can be handled
        # later through retry/event-based compensation.
        # -----------------------------------------------------

        try:

            clear_cart(
                user_id=user_id,
            )

        except Exception:

            # Do not invalidate a successfully completed order.
            #
            # In a later production iteration this should be
            # handled with an event/outbox/retry mechanism.

            pass

    return order


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
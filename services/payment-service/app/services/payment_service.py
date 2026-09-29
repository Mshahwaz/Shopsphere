import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment
from app.schemas import PaymentCreateRequest


VALID_PAYMENT_STATUSES = {
    "PENDING",
    "PROCESSING",
    "SUCCESS",
    "FAILED",
}


ALLOWED_PAYMENT_TRANSITIONS = {
    "PENDING": {
        "PROCESSING",
    },
    "PROCESSING": {
        "SUCCESS",
        "FAILED",
    },
    "SUCCESS": set(),
    "FAILED": set(),
}


def create_payment(
    db: Session,
    request: PaymentCreateRequest
) -> Payment:
    
    existing_payment = db.scalar(
        select(Payment).where(
            Payment.order_id == request.order_id
        )
    )

    if existing_payment is not None:
        raise ValueError(
            "Payment already exists for this order"
        )

    payment = Payment(
        order_id=request.order_id,
        amount=request.amount,
        status="PENDING",
    )

    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise

    return payment

def update_payment_status(
    db: Session,
    payment_id: uuid.UUID,
    new_status: str,
) -> Payment | None:

    if new_status not in VALID_PAYMENT_STATUSES:
        raise ValueError(
            "Invalid payment status"
        )

    payment = db.scalar(
        select(Payment).where(
            Payment.id == payment_id
        )
    )

    if payment is None:
        return None

    allowed_statuses = ALLOWED_PAYMENT_TRANSITIONS.get(
        payment.status,
        set(),
    )

    if new_status not in allowed_statuses:
        raise ValueError(
            f"Cannot change payment status "
            f"from {payment.status} to {new_status}"
        )

    payment.status = new_status

    try:
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise

    return payment
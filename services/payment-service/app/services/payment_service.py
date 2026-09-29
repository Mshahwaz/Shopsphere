import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Payment
from app.schemas import PaymentCreateRequest

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
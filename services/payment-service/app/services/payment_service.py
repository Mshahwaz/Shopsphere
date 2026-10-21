import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session
from decimal import Decimal

from app.models import Payment
from app.schemas import (
    PaymentCreateRequest,
    PaymentVerificationRequest,
)
from app.providers.mock import MockPaymentProvider
from app.providers.razorpay_provider import RazorpayPaymentProvider

# payment_provider =  MockPaymentProvider()
payment_provider =  RazorpayPaymentProvider()



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

def create_checkout(
    db: Session,
    request: PaymentCreateRequest,
) -> Payment:
    """
    Create a ShopSphere payment and its corresponding Razorpay order.

    Reuse an existing checkout when the same order requests checkout again.
    """

    existing_payment = db.scalar(
        select(Payment).where(
            Payment.order_id == request.order_id
        )
    )

    if existing_payment is not None:
        if existing_payment.amount != request.amount:
            raise ValueError(
                "Payment already exists with a different amount"
            )

        if existing_payment.status != "PENDING":
            raise ValueError(
                f"Cannot create checkout for payment "
                f"with status {existing_payment.status}"
            )

        if not existing_payment.provider_order_id:
            raise ValueError(
                "Checkout is incomplete; payment recovery is required"
            )

        return existing_payment

    payment = create_payment(
        db=db,
        request=request,
    )

    try:
        provider_order = payment_provider.create_order(
            payment_id=str(payment.id),
            amount=payment.amount,
        )

        provider_order_id = provider_order.get("id")

        if not provider_order_id:
            raise ValueError(
                "Payment provider did not return an order ID"
            )

        payment.provider_order_id = provider_order_id

        db.commit()
        db.refresh(payment)

        return payment

    except Exception:
        db.rollback()
        raise

def verify_payment(
    db: Session,
    payment_id: uuid.UUID,
    request: PaymentVerificationRequest,
) -> Payment | None:
    """
    Verify a Razorpay Checkout response and persist the payment result.
    """

    payment = db.scalar(
        select(Payment)
        .where(Payment.id == payment_id)
        .with_for_update()
    )

    if payment is None:
        return None

    if payment.status == "SUCCESS":
        if (
            request.provider_order_id != payment.provider_order_id
            or request.provider_payment_id != payment.provider_payment_id
        ):
            raise ValueError(
                "Payment verification identifiers do not match "
                "the stored successful payment"
            )

        return payment

    if payment.status != "PENDING":
        raise ValueError(
            f"Cannot verify payment from status {payment.status}"
        )

    if not payment.provider_order_id:
        raise ValueError(
            "Payment does not have a Razorpay order ID"
        )

    if request.provider_order_id != payment.provider_order_id:
        raise ValueError(
            "Razorpay order ID does not match the stored order"
        )

    try:
        signature_valid = payment_provider.verify_payment(
            provider_order_id=request.provider_order_id,
            provider_payment_id=request.provider_payment_id,
            signature=request.signature,
        )

        if not signature_valid:
            raise ValueError("Invalid Razorpay payment signature")

        provider_payment = payment_provider.fetch_payment(
            request.provider_payment_id
        )

        if provider_payment.get("id") != request.provider_payment_id:
            raise ValueError("Razorpay payment ID mismatch")

        if provider_payment.get("order_id") != payment.provider_order_id:
            raise ValueError("Razorpay payment belongs to a different order")

        expected_amount_paise = int(payment.amount * 100)

        if provider_payment.get("amount") != expected_amount_paise:
            raise ValueError("Razorpay payment amount does not match")

        if provider_payment.get("currency") != "INR":
            raise ValueError("Unexpected payment currency")

        provider_status = provider_payment.get("status")

        if provider_status == "captured":
            payment.status = "SUCCESS"
        elif provider_status == "failed":
            payment.status = "FAILED"
        else:
            raise ValueError(
                f"Payment has not reached a terminal state: "
                f"{provider_status}"
            )

        payment.provider_payment_id = request.provider_payment_id

        db.commit()
        db.refresh(payment)

        return payment

    except Exception:
        db.rollback()
        raise

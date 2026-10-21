import uuid

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    PaymentCreateRequest,
    PaymentResponse,
    PaymentCheckoutResponse,
    PaymentVerificationRequest,
    # PaymentProcessRequest
)
from app.services.payment_service import (
    create_payment,
    create_checkout,
    verify_payment,
    )
from app.security import verify_service_token
from app.config import settings

router = APIRouter(
    prefix="/api/v1/payments",
    tags=["Payments"],
)

@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_payment_endpoint(
    request: PaymentCreateRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_token),
):
    try:
        return create_payment(
            db=db,
            request=request,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/checkout",
    response_model=PaymentCheckoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_checkout_endpoint(
    request: PaymentCreateRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_token),
):
    try:
        payment = create_checkout(
            db=db,
            request=request,
        )

        return PaymentCheckoutResponse(
            payment_id=payment.id,
            order_id=payment.order_id,
            amount=payment.amount,
            status=payment.status,
            provider_order_id=payment.provider_order_id,
            provider_key_id=settings.razorpay_key_id,
            currency="INR",
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

@router.post(
    "/{payment_id}/verify",
    response_model=PaymentResponse,
)
def verify_payment_endpoint(
    payment_id: uuid.UUID,
    request: PaymentVerificationRequest,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_service_token),
):
    try:
        payment = verify_payment(
            db=db,
            payment_id=payment_id,
            request=request,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment
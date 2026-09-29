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
    PaymentStatusUpdateRequest
)
from app.services.payment_service import create_payment, update_payment_status

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


@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
)
def update_payment_status_endpoint(
    payment_id: uuid.UUID,
    request: PaymentStatusUpdateRequest,
    db: Session = Depends(get_db),
):
    try:
        payment = update_payment_status(
            db=db,
            payment_id=payment_id,
            new_status=request.status,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )

    return payment
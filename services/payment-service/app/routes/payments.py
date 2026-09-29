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
)
from app.services.payment_service import create_payment

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
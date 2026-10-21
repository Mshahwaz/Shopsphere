import uuid
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class PaymentCreateRequest(BaseModel):
    order_id: uuid.UUID
    amount: Decimal = Field(gt=0)


class PaymentResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal
    status: str

    model_config = {
        "from_attributes": True,
    }


class PaymentStatusUpdateRequest(BaseModel):
    status: str


class PaymentCheckoutResponse(BaseModel):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal
    status: str
    provider_order_id: str
    provider_key_id: str
    currency: str = "INR"

    model_config = {
        "from_attributes": True,
    }


class PaymentVerificationRequest(BaseModel):
    provider_order_id: str = Field(min_length=1)
    provider_payment_id: str = Field(min_length=1)
    signature: str = Field(min_length=1)
import uuid
from decimal import Decimal

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
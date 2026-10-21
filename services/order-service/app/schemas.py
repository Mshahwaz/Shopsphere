import uuid
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field

class OrderItemResponse(BaseModel):
    id: uuid.UUID
    order_id: uuid.UUID
    product_id: uuid.UUID
    product_name: str
    unit_price: Decimal
    quantity: int

    model_config = {
        "from_attributes": True,
    }


class OrderResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    items: list[OrderItemResponse]

class CheckoutDetailsResponse(BaseModel):
    payment_id: uuid.UUID
    order_id: uuid.UUID
    amount: Decimal
    status: str
    provider_order_id: str
    provider_key_id: str
    currency: str


class OrderCheckoutResponse(BaseModel):
    order: OrderResponse
    checkout: CheckoutDetailsResponse

class PaymentVerificationRequest(BaseModel):
    provider_order_id: str
    provider_payment_id: str
    signature: str

class OrderSummaryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }

class OrderStatusUpdateRequest(BaseModel):
    status: str

class OrderPaymentVerificationRequest(BaseModel):
    payment_id: uuid.UUID
    provider_order_id: str
    provider_payment_id: str
    signature: str
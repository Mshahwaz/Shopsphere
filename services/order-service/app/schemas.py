import uuid
from decimal import Decimal
from datetime import datetime

from pydantic import BaseModel, Field


class OrderItemCreateRequest(BaseModel):
    product_id: uuid.UUID
    product_name: str = Field(
        min_length=1,
        max_length=255,
    )
    unit_price: Decimal = Field(
        gt=0,
    )
    quantity: int = Field(
        gt=0,
    )


class OrderCreateRequest(BaseModel):
    user_id: uuid.UUID
    items: list[OrderItemCreateRequest] = Field(
        min_length=1,
    )


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

class OrderSummaryResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: str
    total_amount: Decimal
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
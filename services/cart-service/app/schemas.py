import uuid

from pydantic import BaseModel, Field


class CartItemCreateRequest(BaseModel):
    product_id: uuid.UUID
    quantity: int = Field(gt=0)


class CartItemResponse(BaseModel):
    id: uuid.UUID
    cart_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int

    model_config = {
        "from_attributes": True,
    }
    
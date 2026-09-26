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
    
class CartResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    items: list[CartItemResponse]

    model_config = {
        "from_attributes": True,
    }
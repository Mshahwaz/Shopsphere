import uuid

from decimal import Decimal

from pydantic import BaseModel, Field

class ProductCreateRequest(BaseModel):
    category_id: uuid.UUID
    name: str = Field(min_length=1,max_length=255)
    description: str | None = None
    price: Decimal = Field(gt=0)

class ProductResponse(BaseModel):
    id: uuid.UUID
    category_id: uuid.UUID
    name: str
    description: str | None
    price: Decimal
    is_active: bool

    model_config = {
        "from_attributes": True
    }
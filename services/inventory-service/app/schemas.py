import uuid
from pydantic import BaseModel, Field


class StockUpdateRequest(BaseModel):
    quantity: int = Field(
        gt=0,
    )

class InventoryResponse(BaseModel):
    id: uuid.UUID
    product_id: uuid.UUID
    available_quantity: int
    reserved_quantity: int

    model_config = {
        "from_attributes": True,
    }

class ReservationRequest(BaseModel):
    quantity: int = Field(
        gt=0,
    )
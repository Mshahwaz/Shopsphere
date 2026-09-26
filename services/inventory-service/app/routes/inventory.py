import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    InventoryResponse,
    StockUpdateRequest,
)
from app.services.inventory_service import add_stock


router = APIRouter(
    prefix="/api/v1/inventory",
    tags=["Inventory"],
)


@router.post(
    "/{product_id}/stock",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
def add_stock_endpoint(
    product_id: uuid.UUID,
    request: StockUpdateRequest,
    db: Session = Depends(get_db),
):
    return add_stock(
        db=db,
        product_id=product_id,
        quantity=request.quantity,
    )
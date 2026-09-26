import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    InventoryResponse,
    StockUpdateRequest,
)
from app.services.inventory_service import add_stock,get_inventory_by_product_id


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

@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
)
def get_inventory_endpoint(
    product_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    inventory = get_inventory_by_product_id(
        db=db,
        product_id=product_id,
    )

    if inventory is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory not found",
        )

    return inventory

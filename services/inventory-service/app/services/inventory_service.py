import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Inventory


def add_stock(
    db: Session,
    product_id: uuid.UUID,
    quantity: int,
) -> Inventory:

    inventory = db.scalar(
        select(Inventory).where(
            Inventory.product_id == product_id
        )
    )

    if inventory is None:
        inventory = Inventory(
            product_id=product_id,
            available_quantity=quantity,
            reserved_quantity=0,
        )

        db.add(inventory)

    else:
        inventory.available_quantity += quantity

    db.commit()
    db.refresh(inventory)

    return inventory

def get_inventory_by_product_id(
    db: Session,
    product_id: uuid.UUID,
) -> Inventory | None:

    return db.scalar(
        select(Inventory).where(
            Inventory.product_id == product_id
        )
    )

def reserve_stock(
    db: Session,
    product_id: uuid.UUID,
    quantity: int,
) -> Inventory | None:

    inventory = db.scalar(
        select(Inventory)
        .where(
            Inventory.product_id == product_id
        )
        .with_for_update()
    )

    if inventory is None:
        return None

    if inventory.available_quantity < quantity:
        raise ValueError("Insufficient stock")

    inventory.available_quantity -= quantity
    inventory.reserved_quantity += quantity

    try:
        db.commit()
        db.refresh(inventory)
    except Exception:
        db.rollback()
        raise

    return inventory
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
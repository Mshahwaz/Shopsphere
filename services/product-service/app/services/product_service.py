import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product
from app.schemas import ProductCreateRequest

def create_product(
    db: Session,
    request: ProductCreateRequest,
    ) -> Product:

    product=Product(
        category_id=request.category_id,
        name=request.name,
        description=request.description,
        price=request.price,
        is_active=True,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_product_by_id(
    db: Session,
    product_id: uuid.UUID,
    ) -> Product | None:
    return db.scalar(
        select(Product).where(
            Product.id == product_id
        )
    )

def get_products(
    db: Session,
    active_only: bool = True,
    category_id: uuid.UUID | None = None
    ) -> list[Product]:

    query=select(Product)

    if active_only:
        query = query.where(
            Product.is_active.is_(True)
        )
    
    if category_id is not None:
        query=query.where(
            Product.category_id == category_id
        )
    
    
    return list(
        db.scalars(query).all()
    )
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Product, Category
from app.schemas import ProductCreateRequest, ProductUpdateRequest

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

def update_product(
    db: Session,
    product_id: uuid.UUID,
    request: ProductUpdateRequest
) -> Product | None:

    product=get_product_by_id(db=db,product_id=product_id)

    if product is None:
        return None
    
    if request.name is not None:
        product.name=request.name
    
    if request.description is not None:
        product.description=request.description

    if request.price is not None:
        product.price=request.price

    db.commit()
    db.refresh(product)
    return product

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

def create_category(
    db: Session,
    name: str
    ):
    category=Category(
        name=name
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category

def get_category_by_id(
    db: Session,
    category_id: uuid.UUID
    ) -> Category | None:

    return db.scalar(
        select(Category).where(
        Category.id == category_id
    )
    )

def get_categories(
    db: Session,
    ) -> list[Category]:

    return list(
        db.scalars(
            select(Category).order_by(Category.name)
        ).all()
    )
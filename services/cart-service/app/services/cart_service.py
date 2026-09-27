import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cart, CartItem

def get_or_create_cart(
    db: Session,
    user_id: uuid.UUID,
) -> Cart:

    cart = db.scalar(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    if cart is None:
        cart = Cart(
            user_id=user_id,
        )

        db.add(cart)
        db.flush()

    return cart

def add_item_to_cart(
    db: Session,
    user_id: uuid.UUID,
    product_id: uuid.UUID,
    quantity: int,
) -> CartItem:

    cart = get_or_create_cart(
        db=db,
        user_id=user_id,
    )

    cart_item = db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id,
        )
    )

    if cart_item is None:
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=product_id,
            quantity=quantity,
        )

        db.add(cart_item)

    else:
        cart_item.quantity += quantity

    db.commit()
    db.refresh(cart_item)

    return cart_item

def get_cart(
    db: Session,
    user_id: uuid.UUID,
    ) -> tuple[Cart, list[CartItem]] | None:
    
    cart=db.scalar(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    if cart is None:
        return None

    items = list(
        db.scalars(
            select(CartItem)
            .where(
                CartItem.cart_id == cart.id
            )
            .order_by(CartItem.created_at)
        ).all()
    )
    return cart, items

def update_cart_item_quantity(
    db: Session,
    user_id: uuid.UUID,
    product_id: uuid.UUID,
    quantity: int
    ) -> CartItem | None:

    cart=db.scalar(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )
    
    if cart is None:
        return None

    cart_item=db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )

    if cart_item is None:
        return None

    cart_item.quantity = quantity
    
    db.commit()
    db.refresh(cart_item)

    return cart_item

def remove_cart_item(
    db: Session,
    user_id: uuid.UUID,
    product_id: uuid.UUID
) -> bool :
    cart = db.scalar(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    if cart is None:
        return False

    cart_item=db.scalar(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == product_id
        )
    )

    if cart_item is None:
        return False

    db.delete(cart_item)
    db.commit()

    return True

def clear_cart(
    db: Session,
    user_id: uuid.UUID
) -> bool:

    cart=db.scalar(
        select(Cart).where(
            Cart.user_id == user_id
        )
    )

    if cart is None:
        return False

    items = list(
        db.scalars(
            select(CartItem)
            .where(
                CartItem.cart_id == cart.id
            )
        ).all()
    )

    for item in items:
        db.delete(item)

    db.commit()
    
    return True


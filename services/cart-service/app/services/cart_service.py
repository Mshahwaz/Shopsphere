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
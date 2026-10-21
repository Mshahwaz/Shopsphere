import uuid

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    CheckoutDetailsResponse,
    OrderCheckoutResponse,
    OrderItemResponse,
    OrderResponse,
    OrderSummaryResponse,
    OrderPaymentVerificationRequest,
)

from app.services.order_service import (
    create_order,
    get_order_for_user,
    get_order_items,
    get_order_by_user,
    confirm_order_after_payment,
)

from app.clients.exceptions import (
    ProductNotFoundError,
    ProductServiceError,
    ProductServiceTimeoutError,
    ProductServiceUnavailableError,
    InsufficientStockError,
    InventoryNotFoundError,
    InventoryServiceError,
    InventoryServiceTimeoutError,
    InventoryServiceUnavailableError,
    PaymentFailedError,
    PaymentNotFoundError,
    PaymentServiceTimeoutError,
    PaymentServiceUnavailableError,
    PaymentServiceError,
    PaymentCheckoutOutcomeUnknownError,
    CartNotFoundError,
    CartServiceError,
    CartServiceTimeoutError,
    CartServiceUnavailableError,
    EmptyCartError,
)

from app.security import get_current_user
from app.clients.payment_client import verify_payment

router = APIRouter(
    prefix="/api/v1/orders",
    tags=["Orders"],
)


# ---------------------------------------------------------
# Create Order
# ---------------------------------------------------------

@router.post(
    "",
    response_model=OrderCheckoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_order_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    try:
        order, checkout = create_order(
            db=db,
            user_id=user_id,
        )
    except EmptyCartError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    except CartNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except CartServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except CartServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except CartServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )
    except ProductNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except ProductServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except ProductServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except ProductServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except InventoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )

    except InsufficientStockError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    except InventoryServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except InventoryServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except InventoryServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except PaymentFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=str(exc),
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    except PaymentServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=str(exc),
        )

    except PaymentServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )

    except PaymentCheckoutOutcomeUnknownError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail={
                "code": "PAYMENT_CHECKOUT_OUTCOME_UNKNOWN",
                "message": str(exc),
            },
        ) from exc

    except PaymentServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    items = [
        OrderItemResponse.model_validate(item)
        for item in order_items_for_response(
            db=db,
            order_id=order.id,
        )
    ]

    return OrderCheckoutResponse(
        order=OrderResponse(
            id=order.id,
            user_id=order.user_id,
            status=order.status,
            total_amount=order.total_amount,
            items=items,
        ),
        checkout=CheckoutDetailsResponse.model_validate(checkout),
    )


# ---------------------------------------------------------
# Helper: Order Items
# ---------------------------------------------------------

def order_items_for_response(
    db: Session,
    order_id,
):
    from sqlalchemy import select
    from app.models import OrderItem

    return db.scalars(
        select(OrderItem)
        .where(
            OrderItem.order_id == order_id
        )
        .order_by(OrderItem.created_at)
    ).all()


# ---------------------------------------------------------
# Get Single Order
# ---------------------------------------------------------

@router.get(
    "/{order_id}",
    response_model=OrderResponse,
)
def get_order_endpoint(
    order_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    order = get_order_for_user(
        db=db,
        order_id=order_id,
        user_id=user_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    items = get_order_items(
        db=db,
        order_id=order.id,
    )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        status=order.status,
        total_amount=order.total_amount,
        items=[
            OrderItemResponse.model_validate(item)
            for item in items
        ],
    )


# ---------------------------------------------------------
# List Current User's Orders
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[OrderSummaryResponse],
)
def list_orders_endpoint(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    return get_order_by_user(
        db=db,
        user_id=user_id,
    )


# ---------------------------------------------------------
# Verify Order Payment
# ---------------------------------------------------------

@router.post("/{order_id}/verify-payment")
def verify_order_payment_endpoint(
    order_id: uuid.UUID,
    request: OrderPaymentVerificationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = uuid.UUID(current_user["user_id"])

    # 1. Confirm that this order belongs to the authenticated user.
    order = get_order_for_user(
        db=db,
        order_id=order_id,
        user_id=user_id,
    )

    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # 2. Do not initiate verification for an order that is
    # already in a terminal state.
    if order.status != "PENDING":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot verify payment for order with status {order.status}",
        )

    # 3. Ask the Payment Service to verify the Razorpay result.
    try:
        payment = verify_payment(
            payment_id=request.payment_id,
            provider_order_id=request.provider_order_id,
            provider_payment_id=request.provider_payment_id,
            signature=request.signature,
        )

    except PaymentNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        ) from exc

    except PaymentServiceTimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Payment verification timed out; check payment status before retrying",
        ) from exc

    except PaymentServiceUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment Service is unavailable",
        ) from exc

    except PaymentServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Payment verification could not be completed",
        ) from exc

    # 4. Verify that the payment belongs to this specific order.
    if str(payment.get("order_id")) != str(order.id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Payment does not belong to this order",
        )

    # 5. Require a successful payment before confirming the order.
    if payment.get("status") != "SUCCESS":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "PAYMENT_NOT_SUCCESSFUL",
                "message": (
                    "Payment has not succeeded; "
                    "the order remains pending"
                ),
                "payment_status": payment.get("status"),
            },
        )

    # 6. Confirm the order and finalize reserved inventory.
    try:
        confirmed_order = confirm_order_after_payment(
            db=db,
            order_id=order.id,
            user_id=user_id,
            payment=payment,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        # Do not claim the order was confirmed if confirmation failed.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Payment was verified, but order confirmation "
                "could not be completed. Check the order and "
                "inventory state before retrying."
            ),
        ) from exc

    if confirmed_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found",
        )

    # 7. Return the final order and payment status.
    return {
        "order_id": str(confirmed_order.id),
        "order_status": confirmed_order.status,
        "payment_id": str(payment.get("id")),
        "payment_status": payment.get("status"),
        "message": (
            "Order confirmed successfully"
            if confirmed_order.status == "CONFIRMED"
            else "Order confirmation completed"
        ),
    }
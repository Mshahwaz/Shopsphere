import uuid
import httpx

from app.config import settings
from app.clients.exceptions import (
    PaymentNotFoundError,
    PaymentFailedError,
    PaymentServiceUnavailableError,
    PaymentServiceTimeoutError,
    PaymentServiceError,
)

def create_payment(order_id: uuid.UUID, amount):
    url = f"{settings.payment_service_url}/api/v1/payments"

    try:
        response = httpx.post(
            url,
            json={
                "order_id": str(order_id),
                "amount": str(amount),
            },
            timeout=5.0,
        )

    except httpx.TimeoutException as exc:
        raise PaymentServiceTimeoutError(
            "Payment Service request timed out"
        ) from exc

    except httpx.RequestError as exc:
        raise PaymentServiceUnavailableError(
            "Payment Service is unavailable"
        ) from exc

    if response.status_code == 404:
        raise PaymentNotFoundError("Payment not found")

    if response.status_code >= 500:
        raise PaymentServiceError(
            "Payment Service returned a server error"
        )

    if response.status_code >= 400:
        raise PaymentServiceError(
            "Payment Service returned an unexpected error"
        )

    return response.json()

def process_payment(payment_id: uuid.UUID):
    url = (
        f"{settings.payment_service_url}"
        f"/api/v1/payments/{payment_id}/process"
    )

    try:
        response = httpx.post(
            url,
            timeout=5.0,
        )

    except httpx.TimeoutException as exc:
        raise PaymentServiceTimeoutError(
            "Payment Service request timed out"
        ) from exc

    except httpx.RequestError as exc:
        raise PaymentServiceUnavailableError(
            "Payment Service is unavailable"
        ) from exc

    if response.status_code == 404:
        raise PaymentNotFoundError("Payment not found")

    if response.status_code >= 500:
        raise PaymentServiceError(
            "Payment Service returned a server error"
        )

    if response.status_code >= 400:
        raise PaymentServiceError(
            "Payment Service returned an unexpected error"
        )

    payment = response.json()

    if payment.get("status") == "FAILED":
        raise PaymentFailedError("Payment processing failed")

    return payment
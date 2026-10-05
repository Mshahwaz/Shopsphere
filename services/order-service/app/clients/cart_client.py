import time
import uuid

import httpx

from app.config import settings
from app.clients.exceptions import (
    CartNotFoundError,
    CartServiceError,
    CartServiceTimeoutError,
    CartServiceUnavailableError,
)

def get_cart(user_id: uuid.UUID) -> dict:
    url = (
        f"{settings.cart_service_url}"
        f"/api/v1/internal/cart/{user_id}"
    )

    headers = {
        "X-SERVICE-TOKEN" : settings.cart_service_auth_token,
    }

    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            response = httpx.get(
                url,
                headers=headers,
                timeout=5.0,
            )

            if response.status_code == 200:
                return response.json()

            if response.status_code == 404:
                raise CartNotFoundError(
                    "Cart not found"
                )

            if response.status_code >= 500:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue

                raise CartServiceUnavailableError(
                    "Cart Service is unavailable"
                )

            raise CartServiceError(
                f"Cart Service returned "
                f"status {response.status_code}"
            )

        except httpx.TimeoutException as exc:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue

            raise CartServiceTimeoutError(
                "Cart Service request timed out"
            ) from exc

        except httpx.RequestError as exc:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue

            raise CartServiceUnavailableError(
                "Cart Service is unavailable"
            ) from exc


def clear_cart(user_id: uuid.UUID) -> None:

    url = (
        f"{settings.cart_service_url}"
        f"/api/v1/internal/cart/{user_id}"
    )

    headers = {
        "X-SERVICE-TOKEN": settings.cart_service_auth_token,
    }

    max_retries = 2

    for attempt in range(max_retries + 1):
        try:
            response = httpx.delete(
                url,
                headers=headers,
                timeout=5.0,
            )

            if response.status_code == 204:
                return

            if response.status_code == 404:
                raise CartNotFoundError(
                    "Cart not found"
                )

            if response.status_code >= 500:
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue

                raise CartServiceUnavailableError(
                    "Cart Service is unavailable"
                )

            raise CartServiceError(
                f"Cart Service returned status "
                f"{response.status_code}"
            )

        except httpx.TimeoutException as exc:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue

            raise CartServiceTimeoutError(
                "Cart Service request timed out"
            ) from exc

        except httpx.RequestError as exc:
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                continue

            raise CartServiceUnavailableError(
                "Cart Service is unavailable"
            ) from exc
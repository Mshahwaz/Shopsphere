import uuid
import time
import httpx

from app.config import settings
from app.clients.exceptions import (
    ProductNotFoundError,
    ProductServiceError,
    ProductServiceTimeoutError,
    ProductServiceUnavailableError
)

MAX_RETRIES = 2
RETRY_DELAY = 0.2

def get_product(
    product_id: uuid.UUID
) -> dict:

    url = (
        f"{settings.product_service_url}"
        f"/api/v1/products/{product_id}"
    )
    for attempt in range(MAX_RETRIES + 1):
        try:
            response = httpx.get(
                url,
                timeout=5.0,
            )

            if response.status_code == 404:
                raise ProductNotFoundError(
                    "Product not found"
                )

            if response.status_code >= 500:
                raise ProductServiceError(
                    "Product Service returned a server error"
                )

            if response.status_code >= 400:
                raise ProductServiceError(
                    "Product Service returned an unexpected error"
                )

            return response.json()

        except httpx.TimeoutException as exc:
            if attempt == MAX_RETRIES:
                raise ProductServiceTimeoutError(
                    "Product Service request timed out"
                ) from exc

        except httpx.RequestError as exc:
            if attempt == MAX_RETRIES:
                raise ProductServiceUnavailableError(
                    "Product Service is unavailable"
                ) from exc

        if attempt < MAX_RETRIES:
            time.sleep(
                RETRY_DELAY * (2 ** attempt)
            )

    raise ProductServiceError(
        "Product Service request failed"
    )
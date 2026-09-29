import uuid

import httpx

from app.config import settings
from app.clients.exceptions import (
    ProductNotFoundError,
    ProductServiceError,
    ProductServiceTimeoutError,
    ProductServiceUnavailableError
)

def get_product(
    product_id: uuid.UUID
) -> dict:

    url = (
        f"{settings.product_service_url}"
        f"/api/v1/products/{product_id}"
    )
    try:
        response = httpx.get(
            url=url,
            timeout=5.0
        )
    except httpx.TimeoutException as exc:
        raise ProductServiceTimeoutError(
            "Product Service request timed out"
        ) from exc
    except httpx.RequestError as exc:
        raise ProductServiceUnavailableError(
            "Product Service is unavailable"
        ) from exc
    
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
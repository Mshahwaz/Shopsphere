import uuid

import httpx

from app.config import settings
from app.clients.exceptions import (
    InsufficientStockError,
    InventoryNotFoundError,
    InventoryServiceError,
    InventoryServiceTimeoutError,
    InventoryServiceUnavailableError
)

def reserve_stock(
    product_id: uuid.UUID,
    quantity: int,
):

    url = (
        f"{settings.inventory_service_url}"
        f"/api/v1/inventory/{product_id}/reserve"
    )

    try:
        response = httpx.post(
            url,
            json={"quantity": quantity},
            timeout=5.0,
        )

    except httpx.TimeoutException as exc:
        raise InventoryServiceTimeoutError(
            "Inventory Service request timed out"
        ) from exc

    except httpx.RequestError as exc:
        raise InventoryServiceUnavailableError(
            "Inventory Service is unavailable"
        ) from exc

    if response.status_code == 404:
        raise InventoryNotFoundError(
            "Inventory not found"
        )

    if response.status_code == 409:
        raise InsufficientStockError(
            "Insufficient stock"
        )

    if response.status_code >= 500:
        raise InventoryServiceError(
            "Inventory Service returned a server error"
        )

    if response.status_code >= 400:
        raise InventoryServiceError(
            "Inventory Service returned an unexpected error"
        )

    return response.json()
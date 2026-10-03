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

SERVICE_HEADERS = {
    "X-Service-Token" : settings.inventory_service_auth_token,
}

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
            headers=SERVICE_HEADERS,
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


def release_stock(
    product_id: uuid.UUID,
    quantity: int,
):
    url = f"{settings.inventory_service_url}/api/v1/inventory/{product_id}/release"

    payload = {
        "quantity": quantity
    }

    try:
        response = httpx.post(
            url,
            json=payload,
            headers=SERVICE_HEADERS,
            timeout=5.0,
        )

    except httpx.TimeoutException as exc:
        raise InventoryServiceTimeoutError(
            "Inventory Service timed out while releasing stock"
        ) from exc

    except httpx.RequestError as exc:
        raise InventoryServiceUnavailableError(
            "Inventory Service is unavailable while releasing stock"
        ) from exc

    if response.status_code == 404:
        raise InventoryNotFoundError(
            "Inventory not found"
        )

    if response.status_code == 409:
        raise InventoryServiceError(
            response.json().get(
                "detail",
                "Unable to release inventory"
            )
        )

    if response.status_code >= 500:
        raise InventoryServiceError(
            "Inventory Service returned an internal error"
        )

    if response.status_code >= 400:
        raise InventoryServiceError(
            response.json().get(
                "detail",
                "Inventory release failed"
            )
        )

    return response.json()


def reduce_stock(
    product_id: uuid.UUID,
    quantity: int,
):
    url = (
        f"{settings.inventory_service_url}"
        f"/api/v1/inventory/{product_id}/reduce"
    )

    payload = {
        "quantity": quantity
    }

    try:
        response = httpx.post(
            url=url,
            json=payload,
            headers=SERVICE_HEADERS,
            timeout=5.0
        )

    except httpx.TimeoutException as exc:
        raise InventoryServiceTimeoutError(
            "Inventory Service timed out while reducing stock"
        ) from exc

    except httpx.RequestError as exc:
        raise InventoryServiceUnavailableError(
            "Inventory Service is unavailable while reducing stock"
        ) from exc

    if response.status_code == 404:
        raise InventoryNotFoundError(
            "Inventory not found"
        )

    if response.status_code == 409:
        raise InventoryServiceError(
            response.json().get(
                "detail",
                "Unable to reduce inventory"
            )
        )

    if response.status_code >= 500:
        raise InventoryServiceError(
            "Inventory Service returned an internal error"
        )

    if response.status_code >= 400:
        raise InventoryServiceError(
            response.json().get(
                "detail",
                "Inventory reduction failed"
            )
        )

    return response.json()
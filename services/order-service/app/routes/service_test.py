import uuid

from fastapi import APIRouter, HTTPException, status

from app.clients.exceptions import (
    ProductNotFoundError,
    ProductServiceError,
    ProductServiceTimeoutError,
    ProductServiceUnavailableError,
)
from app.clients.product_client import get_product

router = APIRouter(
    prefix="/api/v1/service-test",
    tags=["Service Communication"],
)

@router.get("/products/{product_id}")
def test_product_service(
    product_id: uuid.UUID,
):
    try:
        return get_product(product_id)

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
from decimal import Decimal
from typing import Any

from app.providers.base import PaymentProvider


class MockPaymentProvider(PaymentProvider):

    def create_order(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> dict[str, Any]:
        return {
            "id": f"mock_order_{payment_id}",
            "amount": int(amount * 100),
            "currency": "INR",
        }

    def verify_payment(
        self,
        provider_order_id: str,
        provider_payment_id: str,
        signature: str,
    ) -> bool:
        # The mock provider does not perform cryptographic verification.
        # Do not use this implementation for real payments.
        return False

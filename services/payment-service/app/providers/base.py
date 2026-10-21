from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Any


class PaymentProvider(ABC):

    @abstractmethod
    def create_order(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> dict[str, Any]:
        """Create a provider order and return its checkout details."""
        raise NotImplementedError

    @abstractmethod
    def verify_payment(
        self,
        provider_order_id: str,
        provider_payment_id: str,
        signature: str,
    ) -> bool:
        """Verify the payment signature returned by the provider."""
        raise NotImplementedError

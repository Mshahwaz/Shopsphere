from abc import ABC, abstractmethod
from decimal import Decimal

class PaymentProvider(ABC):

    @abstractmethod
    def process_payment(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> str:

        """
        Process a payment and return the resulting status.

        Expected statuses:
        SUCCESS
        FAILED
        """
        raise NotImplementedError
from decimal import Decimal

from app.providers.base import PaymentProvider

class MockPaymentProvider(PaymentProvider):

    def process_payment(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> str:
        return "SUCCESS"
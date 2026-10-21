from decimal import Decimal
from typing import Any

import razorpay

from app.config import settings
from app.providers.base import PaymentProvider


class RazorpayPaymentProvider(PaymentProvider):

    def __init__(self) -> None:
        self.client = razorpay.Client(
            auth=(
                settings.razorpay_key_id,
                settings.razorpay_key_secret,
            )
        )

    def create_order(
        self,
        payment_id: str,
        amount: Decimal,
    ) -> dict[str, Any]:

        amount_in_paise = int(amount * 100)

        order = self.client.order.create(
            data={
                "amount": amount_in_paise,
                "currency": "INR",
                "receipt": payment_id,
            }
        )

        return order

    def verify_payment(
        self,
        provider_order_id: str,
        provider_payment_id: str,
        signature: str,
    ) -> bool:

        try:
            self.client.utility.verify_payment_signature(
                {
                    "razorpay_order_id": provider_order_id,
                    "razorpay_payment_id": provider_payment_id,
                    "razorpay_signature": signature,
                }
            )
            return True

        except razorpay.errors.SignatureVerificationError:
            return False

    def fetch_payment(self, provider_payment_id: str) -> dict[str, Any]:
        """
        Fetch payment details from Razorpay.

        Args:
            provider_payment_id: Razorpay payment ID.

        Returns:
            Payment details returned by Razorpay.
        """
        return self.client.payment.fetch(provider_payment_id)
        
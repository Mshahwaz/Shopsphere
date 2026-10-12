import json
import boto3

from app.config import settings


sqs = boto3.client(
    "sqs",
    region_name=settings.aws_region,
    endpoint_url=settings.sqs_endpoint_url,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)


def send_order_confirmation_notification(event):
    payload = event["payload"]

    order_id = payload["order_id"]
    user_id = payload["user_id"]
    total_amount = payload["total_amount"]

    # Simulate sending an order confirmation notification.
    print("\n=== Order Confirmation Notification ===")
    print(f"Order ID: {order_id}")
    print(f"User ID: {user_id}")
    print(f"Order Total: {total_amount}")
    print("Notification status: SIMULATED")
    print("=======================================\n")


def consume_messages():
    print("Notification consumer started")

    while True:
        response = sqs.receive_message(
            QueueUrl=settings.sqs_queue_url,
            MaxNumberOfMessages=5,
            WaitTimeSeconds=20,
        )

        messages = response.get("Messages", [])

        if not messages:
            continue

        for message in messages:
            try:
                event = json.loads(message["Body"])

                event_id = event["event_id"]
                event_type = event["event_type"]
                payload = event["payload"]

                if event_type != "OrderConfirmed":
                    print(f"Unsupported event type: {event_type}")
                    continue

                if not isinstance(payload, dict):
                    print(f"Invalid payload for event: {event_id}")
                    continue

                # Process the business event.
                send_order_confirmation_notification(event)

                # Delete the message only after processing succeeds.
                sqs.delete_message(
                    QueueUrl=settings.sqs_queue_url,
                    ReceiptHandle=message["ReceiptHandle"],
                )

                print(f"Event processed successfully: {event_id}")
                print("SQS message deleted")

            except (json.JSONDecodeError, KeyError, TypeError) as exc:
                print("Invalid event message:", exc)


if __name__ == "__main__":
    consume_messages()
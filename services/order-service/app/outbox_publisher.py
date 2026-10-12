import json
from datetime import datetime, timezone
import time

from botocore.exceptions import BotoCoreError, ClientError
import boto3
from sqlalchemy import select

from app.config import settings
from app.database import SessionLocal
from app.models import OutboxEvent

sqs = boto3.client(
    "sqs",
    region_name=settings.aws_region,
    endpoint_url=settings.sqs_endpoint_url,
    aws_access_key_id="test",
    aws_secret_access_key="test",
)

def publish_pending_events():
    with SessionLocal() as db:
        events = db.scalars(
            select(OutboxEvent)
            .where(OutboxEvent.published_at.is_(None))
            .order_by(OutboxEvent.created_at)
            .limit(10)
        ).all()

        for event in events:
            message = {
                "event_id": str(event.id),
                "event_type": event.event_type,
                "payload": event.payload,
            }

            for attempt in range(3):
                try:
                    sqs.send_message(
                        QueueUrl=settings.sqs_queue_url,
                        MessageBody=json.dumps(message),
                    )
                    break

                except (BotoCoreError, ClientError):
                    if attempt == 2:
                        raise

                    time.sleep(2 ** attempt)

            event.published_at = datetime.now(timezone.utc)
            db.commit()

        return len(events)

if __name__ == "__main__":
    print("Outbox publisher started")

    while True:
        try:
            published_count = publish_pending_events()

            if published_count > 0:
                print(f"Published {published_count} event(s)")

        except Exception as exc:
            print(f"Publisher error: {exc}")

        time.sleep(5)
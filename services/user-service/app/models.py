from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import uuid
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from sqlalchemy import  DateTime, String



class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    auth_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False
    )
    first_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    last_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

# Defines the SQLAlchemy Base class used by all database models
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime

import uuid

Base = declarative_base()


class BaseTimestampModel:
    """
    Base mixin for all models providing automatic timestamp fields.

    Attributes:
        created_at (datetime): The timestamp when the record was created.
        updated_at (datetime): The timestamp when the record was last updated.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class BaseModel(BaseTimestampModel):
    """
    Base model mixin providing a UUID primary key and timestamps.

    Attributes:
        id (uuid.UUID): The unique primary key identifier for the model.
        created_at (datetime): The timestamp when the record was created (from BaseTimestampModel).
        updated_at (datetime): The timestamp when the record was last updated (from BaseTimestampModel).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

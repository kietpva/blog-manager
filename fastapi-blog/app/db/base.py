# Defines the SQLAlchemy Base class used by all database models
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime

import uuid

Base = declarative_base()


class BaseModel:
    """
    Base mixin for all models
    - id (UUID)
    - created_at
    - updated_at
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

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

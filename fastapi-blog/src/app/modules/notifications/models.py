from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from src.app.db.base import BaseModel


class Notification(BaseModel):
    """
    Notification SQLAlchemy model.

    Represents a notification sent to a user.

    Attributes:
        id (uuid.UUID): Primary key, unique identifier (from BaseModel).
        created_at (datetime): Timestamp for when the notification was created (from BaseModel).
        updated_at (datetime): Timestamp for when the notification was last updated (from BaseModel)
        user_id (uuid.UUID): Foreign key referencing the notified user.
        title (str): Short title or heading of the notification.
        content (str): Detailed notification message.
        type (str): Type or category of notification (e.g., "follow", "comment").
        is_read (bool): Whether the user has read the notification.
    """

    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, nullable=False)

    is_read = Column(Boolean, default=False)

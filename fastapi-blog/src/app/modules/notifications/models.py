from sqlalchemy import Boolean, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from src.app.db.base import BaseModel


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(String, nullable=False)

    is_read = Column(Boolean, default=False)

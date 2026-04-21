from sqlalchemy import UUID, UniqueConstraint
from sqlalchemy.orm import mapped_column

from src.app.db.base import BaseModel


class Follow(BaseModel):
    """
    Follow SQLAlchemy model.

    Represents a follow relationship between users.

    Attributes:
        id (uuid.UUID): Unique identifier for the follow (from BaseModel).
        created_at (datetime): Timestamp when the follow was created (from BaseModel).
        updated_at (datetime): Timestamp when the follow was last updated (from BaseModel).
        follower_id (uuid.UUID): The ID of the user who is following.
        following_id (uuid.UUID): The ID of the user being followed.
    """

    __tablename__ = "follows"

    follower_id = mapped_column(UUID(as_uuid=True), nullable=False)
    following_id = mapped_column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (UniqueConstraint("follower_id", "following_id"),)

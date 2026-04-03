import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel, BaseTimestampModel

if TYPE_CHECKING:
    from app.modules.categories.models import Category


class PostCategory(BaseTimestampModel):
    """
    Association table for the many-to-many relationship between posts and categories.

    Represents a mapping between Post and Category entities, allowing each post
    to be associated with multiple categories and vice versa. Inherits timestamps
    for creation and update times.

    Attributes:
        post_id (uuid.UUID): The UUID of the associated post.
        category_id (uuid.UUID): The UUID of the associated category.
        created_at (datetime): Timestamp when the association was created.
        updated_at (datetime): Timestamp when the association was last updated.
    """

    __tablename__ = "post_categories"

    post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("posts.id"),
        primary_key=True,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id"),
        primary_key=True,
    )


class Post(BaseModel):
    """
    SQLAlchemy model for a blog post.

    Represents a blog post entity with a UUID primary key, title, content,
    author ID, and a many-to-many relationship with categories.

    Attributes:
        id (uuid.UUID): The unique identifier for the post, from BaseModel.
        title (str): The title of the post.
        content (str): The textual content of the post.
        author_id (uuid.UUID): The UUID of the user who authored the post.
        categories (list[Category]): List of categories associated via many-to-many relation.
        created_at (datetime): Timestamp when the post was created, from BaseModel.
        updated_at (datetime): Timestamp when the post was last updated, from BaseModel.
    """

    __tablename__ = "posts"
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)

    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    categories: Mapped[list["Category"]] = relationship(
        "Category",
        secondary="post_categories",
        back_populates="posts",
    )

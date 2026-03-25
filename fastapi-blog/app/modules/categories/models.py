from typing import TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, BaseModel

if TYPE_CHECKING:
    from app.modules.posts.models import Post


class Category(Base, BaseModel):
    """
    SQLAlchemy model for a blog/category.

    Represents a category that groups related posts. Each category has a unique name, an optional description,
    and a relationship to the posts assigned to it.

    Attributes:
        id (uuid.UUID): The unique identifier for the category, inherited from BaseModel.
        name (str): The unique name of the category.
        description (str | None): An optional text description of the category.
        posts (list[Post]): The list of posts associated with this category, via a many-to-many relationship.
        created_at (datetime): Timestamp when the category was created, inherited from BaseModel.
        updated_at (datetime): Timestamp when the category was last updated, inherited from BaseModel.
    """

    __tablename__ = "categories"

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    posts: Mapped[list["Post"]] = relationship(
        "Post",
        secondary="post_categories",
        back_populates="categories",
    )

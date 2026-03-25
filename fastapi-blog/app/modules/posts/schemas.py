from pydantic import BaseModel
from pydantic import Field
from uuid import UUID
from datetime import datetime

from app.modules.categories.schemas import CategoryResponse


class PostCreate(BaseModel):
    """
    Schema for creating a new post.

    Fields:
        title (str): The title of the new post.
        content (str): The main body/content of the post.
        category_ids (list[UUID]): List of category IDs to associate with the post.
    """

    title: str
    content: str
    category_ids: list[UUID] = Field(default_factory=list)


class PostUpdate(BaseModel):
    """
    Schema for updating an existing post.

    Attributes:
        title (Optional[str]): The new title of the post, if updating.
        content (Optional[str]): The new content of the post, if updating.
        category_ids (list[UUID]): List of category IDs to associate with the post.
    """

    title: str | None = None
    content: str | None = None
    category_ids: list[UUID] | None = None


class PostResponse(BaseModel):
    """
    Schema representing the API response for a blog post.

    Fields:
        id (UUID): Unique identifier of the post.
        title (str): Title of the post.
        content (str): Main body content of the post.
        author_id (UUID): Unique identifier of the author.
        created_at (datetime): Timestamp when the post was created.
        categories (list[CategoryResponse]): List of categories associated with the post.
    """

    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime
    categories: list[CategoryResponse]

    class Config:
        from_attributes = True

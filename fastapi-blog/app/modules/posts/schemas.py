from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class PostCreate(BaseModel):
    """
    Schema for creating a new post.

    Attributes:
        title (str): The title of the post.
        content (str): The content of the post.
    """

    title: str
    content: str


class PostUpdate(BaseModel):
    """
    Schema for updating an existing post.

    Attributes:
        title (Optional[str]): The new title of the post, if updating.
        content (Optional[str]): The new content of the post, if updating.
    """

    title: str | None = None
    content: str | None = None


class PostResponse(BaseModel):
    """
    Schema for the response data of a post.

    Attributes:
        id (UUID): The unique identifier of the post.
        title (str): The title of the post.
        content (str): The content of the post.
        author_id (UUID): The unique identifier of the post's author.
        created_at (datetime): The datetime when the post was created.
    """

    id: UUID
    title: str
    content: str
    author_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

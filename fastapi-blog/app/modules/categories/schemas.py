import uuid
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """
    Base schema for category data shared by create, update, and response schemas.

    Attributes:
        name (str): The name of the category.
        description (str): The description of the category.
    """

    name: str
    description: str


class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category.

    Attributes:
        name (str): The name of the category.
    """

    pass


class CategoryUpdate(CategoryBase):
    """
    Schema for updating an existing category.

    Attributes:
        name (str): The new name of the category.
    """

    pass


class CategoryResponse(CategoryBase):
    """
    Schema for the response data of a category.

    Attributes:
        id (uuid.UUID): The unique identifier of the category.
        name (str): The name of the category.
    """

    id: uuid.UUID

    class Config:
        from_attributes = True

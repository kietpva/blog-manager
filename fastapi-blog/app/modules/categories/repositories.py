from sqlalchemy.orm import Session
from app.modules.categories.models import Category
from app.db.repositories import BaseRepository


class CategoryRepository(BaseRepository[Category, str]):
    """
    Repository for performing CRUD operations on Category entities.

    Provides methods to create, retrieve, update, and delete categories
    from the database using a SQLAlchemy session.
    """

    model = Category

    def __init__(self, db: Session):
        """
        Initialize the CategoryRepository.

        Args:
            db (Session): The SQLAlchemy session to use for database operations.
        """
        super().__init__(db)

    def get_all(self):
        """
        Retrieve all categories from the database.

        Returns:
            list[Category]: A list of Category objects.
        """
        return super().get_list()

    def get_by_id(self, category_id):
        """
        Retrieve a category by its ID.

        Args:
            category_id: The unique identifier of the category.

        Returns:
            Category or None: The Category object if found, else None.
        """
        return super().get_by_id(category_id)

    def get_by_name(self, name: str) -> Category | None:
        """
        Retrieve a category by its name.

        Args:
            name (str): The name of the category.

        Returns:
            Category or None: The Category object if found, else None.
        """
        return self.db.query(Category).filter(Category.name == name).first()

    def update(self, category: Category, name: str):
        """
        Update the name of an existing category.

        Args:
            category (Category): The Category object to update.
            name (str): The new name for the category.

        Returns:
            Category: The updated Category object.
        """
        category.name = name
        return super().update(category)

    def delete(self, category: Category):
        """
        Delete a category from the database.

        Args:
            category (Category): The Category object to delete.
        """
        super().delete(category)

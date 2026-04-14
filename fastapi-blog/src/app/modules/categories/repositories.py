from src.app.core.base_repository import BaseRepository
from src.app.modules.categories.models import Category


class CategoryRepository(BaseRepository[Category, str]):
    """
    Repository for performing CRUD operations on Category entities.

    Provides methods to create, retrieve, update, and delete categories
    from the database using a SQLAlchemy session.
    """

    model = Category

    # def list(self):
    #     """
    #     Retrieve all categories from the database.

    #     Returns:
    #         list[Category]: A list of Category objects.
    #     """
    #     _, categories = super().list()
    #     return categories

    def get_by_name(self, name: str) -> Category | None:
        """
        Retrieve a category by its name.

        Args:
            name (str): The name of the category.

        Returns:
            Category or None: The Category object if found, else None.
        """
        return self.db.query(self.model).filter(self.model.name == name).first()

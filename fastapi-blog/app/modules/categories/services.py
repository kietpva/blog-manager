from app.core.exceptions import BadRequestError, NotFoundError
from app.modules.categories.models import Category
from app.modules.categories.repositories import CategoryRepository
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryUpdate,
)
from app.utils.helpers import apply_partial_update


class CategoryService:
    """
    Service layer for handling category-related business logic.

    Provides methods to create, retrieve, update, and delete categories
    using the CategoryRepository.
    """

    def __init__(self, repo: CategoryRepository):
        """
        Initialize the CategoryService with a repository.

        Args:
            repo (CategoryRepository): The repository handling data persistence.
        """
        self.repo = repo

    def create(self, data: CategoryCreate) -> Category:
        """
        Create a new category.

        Args:
            data (CategoryCreate): The data required to create a category.

        Returns:
            The created category object.
        """
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise BadRequestError(message="Category name already exists")

        category = Category(name=data.name, description=data.description)

        return self.repo.create(category)

    def list(self) -> list[Category]:
        """
        Retrieve all categories.

        Returns:
            A list of all category objects.
        """
        return self.repo.list()

    def get_by_id(self, category_id) -> Category:
        """
        Retrieve a category by its ID.

        Args:
            category_id: The ID of the category to retrieve.

        Raises:
            NotFoundException: If the category does not exist.

        Returns:
            The category object.
        """
        category = self.repo.get_by_id(category_id)
        if not category:
            raise NotFoundError(message="Category not found")

        return category

    def partial_update(self, category_id: str, data: CategoryUpdate) -> Category:
        """
        Update an existing category.

        Args:
            category_id: The ID of the category to update.
            data (CategoryUpdate): The data for updating the category.

        Returns:
            The updated category object.
        """
        category = self.get_by_id(category_id)
        existing = self.repo.get_by_name(data.name)
        if existing and existing.id != category.id:
            raise BadRequestError(message="Category name already exists")

        apply_partial_update(
            instance=category,
            data=data.model_dump(exclude_unset=True),
        )

        return self.repo.partial_update(category)

    def delete_category(self, category_id):
        """
        Delete a category by its ID.

        Args:
            category_id: The ID of the category to delete.
        """
        category = self.get_by_id(category_id)
        self.repo.delete(category)

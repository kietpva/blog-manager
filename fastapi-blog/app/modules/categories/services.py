from app.modules.categories.models import Category
from app.modules.categories.repositories import CategoryRepository
from app.modules.categories.schemas import CategoryCreate, CategoryUpdate
from app.core.exceptions import AppError, ErrorCode, NotFoundException, StatusCode


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

    def create_category(self, data: CategoryCreate):
        """
        Create a new category.

        Args:
            data (CategoryCreate): The data required to create a category.

        Returns:
            The created category object.
        """
        existing = self.repo.get_by_name(data.name)
        if existing:
            raise AppError(
                code=ErrorCode.bad_request,
                message="Category name already exists",
                status_code=StatusCode.bad_request,
            )

        category = Category(name=data.name, description=data.description)
        return self.repo.create(category)

    def get_categories(self):
        """
        Retrieve all categories.

        Returns:
            A list of all category objects.
        """
        return self.repo.get_all()

    def get_category(self, category_id):
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
            raise NotFoundException("Category not found")
        return category

    def update_category(self, category_id, data: CategoryUpdate):
        """
        Update an existing category.

        Args:
            category_id: The ID of the category to update.
            data (CategoryUpdate): The data for updating the category.

        Returns:
            The updated category object.
        """
        category = self.get_category(category_id)
        existing = self.repo.get_by_name(data.name)
        if existing and existing.id != category.id:
            raise AppError(
                code=ErrorCode.bad_request,
                message="Category name already exists",
                status_code=StatusCode.bad_request,
            )
        return self.repo.update(category, data.name)

    def delete_category(self, category_id):
        """
        Delete a category by its ID.

        Args:
            category_id: The ID of the category to delete.
        """
        category = self.get_category(category_id)
        self.repo.delete(category)

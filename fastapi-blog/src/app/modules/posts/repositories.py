from __future__ import annotations

from uuid import UUID

from src.app.core.base_repository import BaseRepository
from src.app.core.decorators.retry import RetryFactory
from src.app.modules.categories.models import Category
from src.app.modules.posts.models import Post


class PostRepository(BaseRepository[Post, UUID]):
    search_fields = ["title", "content"]
    """
    Repository for handling CRUD operations for Post entities.
    """

    model = Post

    @RetryFactory.repository()
    def get_categories_by_ids(self, category_ids: list[UUID]) -> list[Category]:
        """
        Retrieve categories by a list of category IDs.

        Args:
            category_ids (list[UUID]): A list of category UUIDs to retrieve.

        Returns:
            list[Category]: A list of Category instances matching the provided IDs.
                            Returns an empty list if no IDs are provided.
        """
        if not category_ids:
            return []

        return self.db.query(Category).filter(Category.id.in_(category_ids)).all()

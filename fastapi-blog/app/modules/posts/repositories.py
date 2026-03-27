from __future__ import annotations

from uuid import UUID
from sqlalchemy.orm import selectinload
from app.modules.posts.models import Post
from app.modules.categories.models import Category
from app.db.repositories import BaseRepository
from app.utils.pagination import PaginationInfo


class PostRepository(BaseRepository[Post, UUID]):
    """
    Repository for handling CRUD operations for Post entities.
    """

    model = Post

    def list(self, limit: int, offset: int) -> tuple[PaginationInfo, list[Post]]:
        """
        Retrieve a paginated list of posts with their associated categories.

        Args:
            limit (int): Maximum number of posts to return.
            offset (int): Number of posts to skip before starting to collect the result set.

        Returns:
            tuple[PaginationInfo, list[Post]]: (pagination, items)
        """
        return super().list(
            limit,
            offset,
            order_by=Post.created_at.desc(),
            options=[selectinload(Post.categories)],
        )

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

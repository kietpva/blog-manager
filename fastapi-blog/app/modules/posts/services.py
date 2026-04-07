from uuid import UUID

from app.core.base_service import BaseService
from app.core.constants import SortOrder
from app.core.exceptions import NotFoundError
from app.modules.posts.models import Post
from app.modules.posts.repositories import PostRepository
from app.modules.posts.schemas import PostCreate, PostUpdate
from app.utils.helpers import apply_partial_update
from app.utils.pagination import PaginationInfo


class PostService(BaseService):
    """
    Service layer for managing posts.

    This class provides methods to create, retrieve, update, and delete posts.
    It utilizes a repository for data access and enforces permission checks
    and error handling for post-related operations.
    """

    def __init__(self, repo: PostRepository):
        """
        Initialize PostService with a post repository.

        Args:
            repo (PostRepository): The repository used for database operations related to posts.
        """
        self.repo = repo

    def create(self, payload: PostCreate, author_id: UUID) -> Post:
        """
        Create a new post with the given payload and author ID.

        Args:
            payload (PostCreate): Data required to create a post.
            author_id (UUID): The ID of the user authoring the post.

        Returns:
            Post: The newly created post instance.
        """
        categories = self.repo.get_categories_by_ids(payload.category_ids)
        if len(categories) != len(set(payload.category_ids)):
            raise NotFoundError(message="One or more categories not found")

        post = Post(
            **payload.model_dump(exclude={"category_ids"}),
            author_id=author_id,
            categories=categories,
        )

        return self.repo.create(post)

    def get_by_id(self, post_id: UUID) -> Post:
        """
        Retrieve a post by its ID.

        Args:
            post_id (UUID): The unique identifier of the post.

        Returns:
            Post: The post instance corresponding to the given ID.

        Raises:
            NotFoundException: If the post is not found.
        """
        post = self.repo.get_by_id(post_id)

        if not post:
            raise NotFoundError(message="Post not found")
        return post

    def list(
        self,
        limit: int,
        offset: int,
        order_by: SortOrder = SortOrder.NEWEST,
    ) -> tuple[PaginationInfo, list[Post]]:
        """
        Retrieve a paginated list of posts, including pagination metadata.

        Args:
            limit (int): Maximum number of posts to return in the response.
            offset (int): Number of posts to skip before starting to collect the result set.

        Returns:
            tuple[PaginationInfo, list[Post]]: Pagination metadata and list of Post instances.
        """

        return self.repo.list(limit, offset, order_by=order_by)

    def partial_update(self, post_id: UUID, payload: PostUpdate, current_user) -> Post:
        """
        Update an existing post's details.

        This method updates a post with the provided data after verifying that the
        current user has permission to perform the operation. If `category_ids` are
        provided in the update payload, validates all referenced categories exist
        before applying changes.

        Args:
            post_id (UUID): The unique identifier of the post to update.
            payload (PostUpdate): The update data for the post (fields to update).
            current_user: The user attempting to update the post.

        Returns:
            Post: The updated Post instance.

        Raises:
            AppError: If the user does not have permission to update the post.
            NotFoundException: If the post or any category is not found.
        """

        post = self.get_by_id(post_id)

        self._check_is_admin_or_owner(
            current_user=current_user, owner_id=post.author_id
        )

        data = payload.model_dump(exclude_unset=True)
        category_ids = data.pop("category_ids", None)

        if category_ids is not None:
            categories = self.repo.get_categories_by_ids(category_ids)
            if len(categories) != len(set(category_ids)):
                raise NotFoundError(message="One or more categories not found")
            post.categories = categories

        apply_partial_update(instance=post, data=data)

        return self.repo.partial_update(post)

    def delete(self, post_id: UUID, current_user):
        """
        Delete a post after checking permissions.

        Args:
            post_id (UUID): The ID of the post to delete.
            current_user: The user attempting the delete operation.

        Raises:
            AppError: If the user does not have permission to delete the post.
        """
        post = self.get_by_id(post_id)

        self._check_is_admin_or_owner(
            current_user=current_user, owner_id=post.author_id
        )

        self.repo.delete(post)

from uuid import UUID

from app.decorators.permissions import check_permission
from app.modules.posts.repositories import PostRepository
from app.modules.posts.schemas import PostCreate, PostUpdate
from app.modules.posts.models import Post
from app.core.exceptions import NotFoundException


class PostService:
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

    def create_post(self, payload: PostCreate, author_id: UUID) -> Post:
        """
        Create a new post with the given payload and author ID.

        Args:
            payload (PostCreate): Data required to create a post.
            author_id (UUID): The ID of the user authoring the post.

        Returns:
            Post: The newly created post instance.
        """
        post = Post(
            title=payload.title,
            content=payload.content,
            author_id=author_id,
        )

        return self.repo.create(post)

    def get_post(self, post_id: UUID) -> Post:
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
            raise NotFoundException(message="Post not found")
        return post

    def get_posts(self):
        """
        Retrieve all posts.

        Returns:
            List[Post]: A list of all posts.
        """
        return self.repo.get_posts()

    def update_post(self, post_id: UUID, payload: PostUpdate, current_user):
        """
        Update a post's details after checking permissions.

        Args:
            post_id (UUID): The ID of the post to update.
            payload (PostUpdate): The update data for the post.
            current_user: The user attempting the update.

        Returns:
            Post: The updated post instance.

        Raises:
            AppError: If the user does not have permission to update the post.
        """

        post = self.get_post(post_id)

        check_permission(current_user, post.author_id)

        data = payload.model_dump(exclude_unset=True)
        for key, value in data.items():
            if hasattr(post, key):
                setattr(post, key, value)

        return self.repo.update(post)

    def delete_post(self, post_id: UUID, current_user):
        """
        Delete a post after checking permissions.

        Args:
            post_id (UUID): The ID of the post to delete.
            current_user: The user attempting the delete operation.

        Raises:
            AppError: If the user does not have permission to delete the post.
        """
        post = self.get_post(post_id)

        check_permission(current_user, post.author_id)

        self.repo.delete(post)

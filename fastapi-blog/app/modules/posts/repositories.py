from sqlalchemy.orm import Session
from uuid import UUID
from sqlalchemy.orm import selectinload
from app.modules.posts.models import Post
from app.modules.categories.models import Category
from app.db.repositories import BaseRepository


class PostRepository(BaseRepository[Post, UUID]):
    """
    Repository for handling CRUD operations for Post entities.
    """

    model = Post

    def __init__(self, db: Session):
        """
        Initialize the PostRepository with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        super().__init__(db)

    def get_by_id(self, post_id: UUID) -> Post | None:
        """
        Retrieve a post by its unique identifier.

        Args:
            post_id (UUID): The unique identifier of the post.

        Returns:
            Post | None: The Post instance if found, otherwise None.
        """
        return (
            self.db.query(Post)
            .options(selectinload(Post.categories))
            .filter(Post.id == post_id)
            .one_or_none()
        )

    def get_posts(self):
        """
        Retrieve all posts from the database.

        Returns:
            list[Post]: A list of all Post instances.
        """
        return self.db.query(Post).options(selectinload(Post.categories)).all()

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

    def update(self, post: Post) -> Post:
        """
        Update an existing post in the database.

        Args:
            post (Post): The Post instance to be updated.

        Returns:
            Post: The updated and refreshed Post instance.
        """
        return super().update(post)

    def delete(self, post: Post):
        """
        Delete a post from the database.

        Args:
            post (Post): The Post instance to be deleted.

        Returns:
            None
        """
        super().delete(post)

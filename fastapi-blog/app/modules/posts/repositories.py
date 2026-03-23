from sqlalchemy.orm import Session
from uuid import UUID
from app.modules.posts.models import Post


class PostRepository:
    """
    Repository for handling CRUD operations for Post entities.
    """

    def __init__(self, db: Session):
        """
        Initialize the PostRepository with a database session.

        Args:
            db (Session): The SQLAlchemy database session.
        """
        self.db = db

    def create(self, post: Post) -> Post:
        """
        Add a new post to the database.

        Args:
            post (Post): The Post instance to be added.

        Returns:
            Post: The newly inserted and refreshed Post instance.
        """
        self.db.add(post)
        self.db.commit()
        self.db.refresh(post)
        return post

    def get_by_id(self, post_id: UUID) -> Post | None:
        """
        Retrieve a post by its unique identifier.

        Args:
            post_id (UUID): The unique identifier of the post.

        Returns:
            Post | None: The Post instance if found, otherwise None.
        """
        return self.db.query(Post).filter(Post.id == post_id).one_or_none()

    def get_posts(self):
        """
        Retrieve all posts from the database.

        Returns:
            list[Post]: A list of all Post instances.
        """
        return self.db.query(Post).all()

    def update(self, post: Post) -> Post:
        """
        Update an existing post in the database.

        Args:
            post (Post): The Post instance to be updated.

        Returns:
            Post: The updated and refreshed Post instance.
        """
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete(self, post: Post):
        """
        Delete a post from the database.

        Args:
            post (Post): The Post instance to be deleted.

        Returns:
            None
        """
        self.db.delete(post)
        self.db.commit()

from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.common import get_db
from app.modules.posts.repositories import PostRepository
from app.modules.posts.services import PostService


def get_post_repository(db: Session = Depends(get_db)) -> PostRepository:
    """
    Dependency to provide a PostRepository instance.

    Args:
        db (Session): The database session obtained from dependency injection.

    Returns:
        PostRepository: An instance of PostRepository using the given database session.
    """
    return PostRepository(db)


def get_post_service(
    repo: PostRepository = Depends(get_post_repository),
) -> PostService:
    """
    Dependency to provide a PostService instance.

    Args:
        repo (PostRepository): The PostRepository instance obtained from dependency injection.

    Returns:
        PostService: An instance of PostService that uses the provided repository.
    """
    return PostService(repo)

from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.core.dependencies import get_db
from src.app.modules.notifications.repository import NotificationRepository
from src.app.modules.notifications.service import NotificationService
from src.app.modules.posts.dependencies import get_post_repository
from src.app.modules.posts.repositories import PostRepository
from src.app.modules.users.dependencies import get_user_repository
from src.app.modules.users.repositories import UserRepository


def get_notification_repository(
    db: Session = Depends(get_db),
) -> NotificationRepository:
    """
    Dependency to provide a NotificationRepository instance.

    Args:
        db (Session): The database session obtained from dependency injection.

    Returns:
        NotificationRepository: An instance of NotificationRepository using
        the given database session.
    """
    return NotificationRepository(db)


def get_notification_service(
    repo: NotificationRepository = Depends(get_notification_repository),
    post_repo: PostRepository = Depends(get_post_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> NotificationService:
    """
    Dependency to provide a NotificationService instance.

    Args:
        repo (NotificationRepository): The NotificationRepository instance obtained
        from dependency injection.

    Returns:
        NotificationService: An instance of NotificationService that uses the provided repository.
    """
    return NotificationService(repo, post_repo, user_repo)

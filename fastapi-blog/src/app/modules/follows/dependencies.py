from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.core.dependencies import get_db
from src.app.modules.follows.repository import FollowRepository
from src.app.modules.follows.services import FollowService
from src.app.modules.notifications.dependencies import get_notification_service
from src.app.modules.notifications.service import NotificationService


def get_follow_repository(db: Session = Depends(get_db)) -> FollowRepository:
    """
    Dependency to provide a FollowRepository instance.

    Args:
        db (Session): The database session obtained from dependency injection.

    Returns:
        FollowRepository: An instance of FollowRepository using the given database session.
    """
    return FollowRepository(db)


def get_follow_service(
    repo: FollowRepository = Depends(get_follow_repository),
    notification_service: NotificationService = Depends(get_notification_service),
) -> FollowService:
    """
    Dependency to provide a FollowService instance.

    Args:
        repo (FollowRepository): The FollowRepository instance obtained from dependency injection.

    Returns:
        FollowService: An instance of FollowService that uses the provided repository.
    """
    return FollowService(repo, notification_service)

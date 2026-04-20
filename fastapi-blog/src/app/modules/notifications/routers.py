from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.app.core.dependencies import get_db
from src.app.modules.notifications.repository import NotificationRepository

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/{user_id}")
def get_notifications(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all notifications for a specified user.

    Args:
        user_id (str): The identifier of the user whose notifications are to be fetched.
        db (Session, optional): Database session dependency.

    Returns:
        list[Notification]: List of notification ORM objects for the user.
    """
    repo = NotificationRepository(db)
    return repo.get_by_user(user_id)

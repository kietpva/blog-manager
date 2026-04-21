from fastapi import APIRouter, Depends, Query

from src.app.core.constants import MAX_ITEMS_PER_PAGE
from src.app.modules.notifications.dependencies import get_notification_service
from src.app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/{user_id}")
def get_notifications(
    user_id: str,
    limit: int = Query(10, ge=1, le=MAX_ITEMS_PER_PAGE),
    offset: int = Query(0, ge=0),
    service: NotificationService = Depends(get_notification_service),
):
    """
    Retrieve all notifications for a specified user.

    Args:
        user_id (str): The identifier of the user whose notifications are to be fetched.
        db (Session, optional): Database session dependency.

    Returns:
        list[Notification]: List of notification ORM objects for the user.
    """
    return service.get_by_user(user_id, limit, offset)

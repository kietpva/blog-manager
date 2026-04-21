from uuid import UUID

from src.app.core.base_repository import BaseRepository
from src.app.core.constants import SortOrder
from src.app.core.decorators.retry import RetryFactory
from src.app.modules.notifications.models import Notification


class NotificationRepository(BaseRepository[Notification, UUID]):
    model = Notification

    @RetryFactory.repository()
    def get_by_user(self, user_id: str, limit: int, offset: int):
        """
        Retrieve all notifications belonging to a specific user.

        Args:
            user_id (str): The ID of the user whose notifications are to be fetched.

        Returns:
            list[Notification]: List of Notification ORM objects for the given user.
        """
        _, notifications = self.list(
            limit=limit,
            offset=offset,
            order_by=SortOrder.NEWEST,
            filters=[Notification.user_id == user_id],
        )
        return notifications

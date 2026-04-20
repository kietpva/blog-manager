from uuid import UUID

from src.app.core.base_repository import BaseRepository
from src.app.modules.notifications.models import Notification


class NotificationRepository(BaseRepository[Notification, UUID]):
    model = Notification

    def get_by_user(self, user_id: str):
        """
        Retrieve all notifications for a given user, sorted by creation time (newest first).

        Args:
            user_id (str): The UUID or identifier of the user.

        Returns:
            list[Notification]: List of Notification ORM objects belonging to the user.
        """
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

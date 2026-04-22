import asyncio
from collections.abc import Iterable
from datetime import UTC, datetime

from src.app.core.base_service import BaseService
from src.app.core.constants import (
    NotificationRecipient,
    NotificationType,
    UserRole,
    WSEvent,
)
from src.app.core.websocket_manager import manager
from src.app.modules.notifications.models import Notification
from src.app.modules.notifications.repository import NotificationRepository
from src.app.modules.notifications.schemas import NotificationWS, WSMessage
from src.app.modules.posts.repositories import PostRepository
from src.app.modules.users.models import User
from src.app.modules.users.repositories import UserRepository


class NotificationService(BaseService):
    def __init__(
        self,
        repo: NotificationRepository,
        post_repo: PostRepository,
        user_repo: UserRepository,
    ):
        super().__init__(repo.db)
        self.repo = repo
        self.post_repo = post_repo
        self.user_repo = user_repo

    def create_daily_report(self):
        """
        Generate and send a daily report notification to all admin users.

        This method calculates the total number of posts created today and sends a
        notification to every user with the admin role using the websocket manager.
        It persists the notifications and commits the transaction.
        """

        today = datetime.now(UTC).date()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())

        total_posts = self.post_repo.count(
            filters=[
                self.post_repo.model.created_at >= start,
                self.post_repo.model.created_at <= end,
            ]
        )

        _, admins = self.user_repo.list(
            filters=[self.user_repo.model.role == UserRole.ADMIN.value]
        )

        recipients = [
            NotificationRecipient(
                user_id=admin.id,
                ws_user_id=admin.auth_id,  # Clerk user_id
            )
            for admin in admins
        ]

        self._create_and_push(
            recipients=recipients,
            title="Daily Report",
            content=f"Today has {total_posts} posts",
            type_=NotificationType.DAILY_REPORT,
        )

        self.commit()

    def get_by_user(self, user_id: str, limit: int, offset: int):
        """
        Retrieve paginated notifications for a specific user.

        Args:
            user_id (str): The identifier of the user.
            limit (int): Maximum number of notifications to return.
            offset (int): Number of notifications to skip.

        Returns:
            list[Notification]: Notification list sorted by newest first.
        """
        return self.repo.get_by_user(user_id, limit, offset)

    def _create_and_push(
        self,
        recipients: Iterable[NotificationRecipient],
        title: str,
        content: str,
        type_: NotificationType,
    ):
        """
        Create notification records for each recipient, persist them,
        and push real-time notification updates via websocket.

        Args:
            recipients (Iterable[NotificationRecipient]): List of recipients, each with user_id
            and ws_user_id.
            title (str): Title of the notification.
            content (str): Main content/message of the notification.
            type_ (str): The notification type key.

        Workflow:
            1. For each recipient with a valid ws_user_id:
                - Create and persist a Notification record.
            2. Flush the session to assign database IDs.
            3. For persisted notifications, transform to websocket schema and assemble payloads.
            4. Use websocket manager to push notifications in real time to connected users.
        """

        notifications: list[tuple[Notification, str]] = []

        # 1. Create notifications
        for recipient in recipients:
            if not recipient.ws_user_id:
                continue

            notification = Notification(
                user_id=recipient.user_id,
                title=title,
                content=content,
                type=type_.value,
            )

            self.repo.create(notification)
            notifications.append((notification, recipient.ws_user_id))

        if notifications:
            self.flush(notifications)

        ws_payloads: list[tuple[str, dict]] = []

        for notification, ws_user_id in notifications:
            noti_schema = NotificationWS.from_model(notification)

            message = WSMessage(
                event=WSEvent.NOTIFICATION_CREATED,
                data=noti_schema.model_dump(mode="json"),
            )

            ws_payloads.append((ws_user_id, message.model_dump()))

        if ws_payloads:
            asyncio.run(self._push_ws(ws_payloads))

    async def _push_ws(self, payloads: list[tuple[str, dict]]):
        """
        Pushes notifications to websocket clients.

        Args:
            payloads (list[tuple[str, dict]]):
                List of (ws_user_id, message_dict) tuples representing the notification data
                for each user.

        This method asynchronously sends each notification payload to
        the corresponding websocket connection(s) using the websocket connection manager.
        """

        await asyncio.gather(
            *[
                manager.send_notification(ws_user_id, message)
                for ws_user_id, message in payloads
            ]
        )

    def create_follow_notification(
        self,
        follower: User,
        following: User,
    ):

        recipients = [
            NotificationRecipient(
                user_id=following.id,
                ws_user_id=following.auth_id,
            )
        ]

        self._create_and_push(
            recipients=recipients,
            title="New follower",
            content=f"{follower.first_name} {follower.last_name} started following you",
            type_=NotificationType.FOLLOW,
        )

        self.commit()

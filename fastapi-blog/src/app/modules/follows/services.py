from uuid import UUID

from sqlalchemy.exc import IntegrityError

from src.app.core.base_service import BaseService
from src.app.core.exceptions import BadRequestError
from src.app.modules.follows.model import Follow
from src.app.modules.follows.repository import FollowRepository
from src.app.modules.notifications.service import NotificationService
from src.app.modules.users.models import User


class FollowService(BaseService):
    def __init__(
        self, repo: FollowRepository, notification_service: NotificationService
    ):
        super().__init__(repo.db)
        self.repo = repo
        self.notification_service = notification_service

    def create(self, follower_id: UUID, following_id: UUID):
        if follower_id == following_id:
            raise BadRequestError(message="Cannot follow yourself")

        existing_follow = (
            self.db.query(Follow)
            .filter(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
            )
            .one_or_none()
        )
        if existing_follow:
            raise BadRequestError(message="Already following this user")

        follow = Follow(follower_id=follower_id, following_id=following_id)

        try:
            self.repo.create(follow)
            result = self.commit_and_refresh(follow)

            follower = self.db.query(User).filter(User.id == follower_id).one_or_none()
            following = (
                self.db.query(User).filter(User.id == following_id).one_or_none()
            )
            if follower and following:
                self.notification_service.create_follow_notification(
                    follower=follower,
                    following=following,
                )

            return result

        except IntegrityError:
            self.rollback()
            raise BadRequestError(message="Already following this user")
        except Exception:
            self.rollback()
            raise

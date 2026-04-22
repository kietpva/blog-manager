from uuid import UUID

from sqlalchemy.exc import IntegrityError

from src.app.core.base_service import BaseService
from src.app.core.exceptions import BadRequestError
from src.app.modules.follows.model import Follow
from src.app.modules.follows.repository import FollowRepository
from src.app.modules.notifications.service import NotificationService


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

        existing_follow = self.repo.get_by_follower_and_following(
            follower_id=follower_id,
            following_id=following_id,
        )
        if existing_follow:
            raise BadRequestError(message="Already following this user")

        follow = Follow(follower_id=follower_id, following_id=following_id)

        try:
            self.repo.create(follow)
            result = self.commit_and_refresh(follow)

            follower = self.repo.get_user_by_id(follower_id)
            following = self.repo.get_user_by_id(following_id)
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

from uuid import UUID

from src.app.core.base_repository import BaseRepository
from src.app.modules.follows.model import Follow
from src.app.modules.users.models import User


class FollowRepository(BaseRepository[Follow, UUID]):
    model = Follow

    def get_by_follower_and_following(
        self, follower_id: UUID, following_id: UUID
    ) -> Follow | None:
        return (
            self.db.query(Follow)
            .filter(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
            )
            .one_or_none()
        )

    def get_user_by_id(self, user_id: UUID) -> User | None:
        return self.db.query(User).filter(User.id == user_id).one_or_none()

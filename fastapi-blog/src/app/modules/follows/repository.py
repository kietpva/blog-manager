from sqlalchemy import UUID

from src.app.core.base_repository import BaseRepository
from src.app.modules.follows.model import Follow


class FollowRepository(BaseRepository[Follow, UUID]):
    model = Follow

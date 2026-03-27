from __future__ import annotations

from app.modules.users.models import User
from app.db.repositories import BaseRepository
from app.utils.pagination import PaginationInfo


class UserRepository(BaseRepository[User, str]):
    model = User

    def get_by_auth_id(self, auth_id: str) -> User | None:
        """
        Retrieve a user by their authentication ID.

        Args:
            auth_id (str): The authentication ID of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return self.db.query(User).filter(User.auth_id == auth_id).one_or_none()

    def list(self, limit: int, offset: int) -> tuple[PaginationInfo, list[User]]:
        """
        Retrieve a paginated list of users.

        Returns:
            tuple[PaginationInfo, list[User]]: (pagination, items)
        """
        return super().list(
            limit,
            offset,
            order_by=User.created_at.desc(),
        )

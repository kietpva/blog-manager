from __future__ import annotations

from src.app.core.base_repository import BaseRepository
from src.app.core.decorators.retry import RetryFactory
from src.app.modules.users.models import User


class UserRepository(BaseRepository[User, str]):
    search_fields = ["email", "first_name", "last_name"]
    model = User

    @RetryFactory.repository()
    def get_by_auth_id(self, auth_id: str) -> User | None:
        """
        Retrieve a user by their authentication ID.

        Args:
            auth_id (str): The authentication ID of the user.

        Returns:
            User | None: The user if found, otherwise None.
        """
        return self.db.query(User).filter(User.auth_id == auth_id).one_or_none()

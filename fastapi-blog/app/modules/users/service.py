from app.modules.users.repository import UserRepository
from app.modules.users.model import User
from app.modules.users.schema import UserCreate


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def create(self, payload: UserCreate) -> User:
        """Create a user in the database"""

        # check user exists
        existing_user = self.repo.get_by_auth_id(payload.auth_id)
        if existing_user:
            return existing_user

        return self.repo.create(payload)

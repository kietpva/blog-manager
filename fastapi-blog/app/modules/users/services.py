from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.decorators.permissions import check_permission
from app.modules.users.models import User, UserRole
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import UserCreate, UserUpdate, AdminUserUpdate


class UserService:
    """
    Service layer for user-related business logic.

    Provides methods for creating users, retrieving user details, updating user information,
    and administrative user updates. Delegates database operations to the UserRepository.
    Handles application exceptions and ensures appropriate error handling for user actions.
    """

    def __init__(self, repo: UserRepository) -> None:
        """
        Initialize the UserService with a UserRepository.
        """
        self.repo = repo

    def create(self, payload: UserCreate) -> User:
        """
        Create a new user if one does not already exist with the given auth_id.
        """
        existing_user = self.repo.get_by_auth_id(payload.auth_id)

        if existing_user:
            return existing_user

        user = User(
            auth_id=payload.auth_id,
            email=str(payload.email),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )

        try:
            return self.repo.create(user)

        except IntegrityError:
            raise AppError(
                code=ErrorCode.bad_request,
                message="User already exists",
                status_code=StatusCode.bad_request,
            )

        except SQLAlchemyError:
            raise AppError(
                code=ErrorCode.internal_server_error,
                message="Failed to create user",
                status_code=StatusCode.internal_server_error,
            )

    def get_user(self, user_id: str) -> User:
        """
        Retrieve the user associated with the given auth_id.
        """
        user = self.repo.get_by_user_id(user_id)

        if not user:
            raise AppError(
                code=ErrorCode.user_not_found,
                message="User not found",
                status_code=StatusCode.not_found,
            )

        return user

    def get_list(self) -> list[User]:
        """
        Retrieve a list of all users.
        """
        return self.repo.get_list()

    def _update_user(self, *, user_id: str, payload: BaseModel) -> User:
        user = self.repo.get_by_user_id(user_id)

        if not user:
            raise AppError(
                code=ErrorCode.user_not_found,
                message="User not found",
                status_code=StatusCode.not_found,
            )

        try:
            return self.repo.update(user, payload)

        except SQLAlchemyError:
            raise AppError(
                code=ErrorCode.internal_server_error,
                message="Failed to update user",
                status_code=StatusCode.internal_server_error,
            )

    def admin_update(
        self,
        *,
        payload: AdminUserUpdate,
        user_id: str,
        current_user: User,
    ) -> User:
        """
        Admin-only: Update a user's information as an administrator.
        """
        if current_user.role != UserRole.admin:
            raise AppError(
                code=ErrorCode.forbidden,
                message="Permission denied",
                status_code=StatusCode.forbidden,
            )

        return self._update_user(user_id=user_id, payload=payload)

    def update(
        self,
        *,
        payload: UserUpdate,
        user_id: str,
        current_user: User,
    ) -> User:
        check_permission(current_user=current_user, owner_id=user_id)

        return self._update_user(user_id=user_id, payload=payload)

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppError, ErrorCode, NotFoundException, StatusCode
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
        Initialize the UserService with a UserRepository instance.

        Args:
            repo (UserRepository): The repository used for user database operations.
        """
        self.repo = repo

    def create(self, payload: UserCreate) -> User:
        """
        Create a new user in the system.

        Args:
            payload (UserCreate): The data required to create a new user.

        Returns:
            User: The newly created user or the existing user if found.

        Raises:
            AppError: If the user already exists (based on the auth_id).
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

    def get_user(self, user_id: str) -> User:
        """
        Retrieve a user by their ID.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            User: The user object if found.

        Raises:
            NotFoundException: If no user exists with the provided ID.
        """
        user = self.repo.get_by_user_id(user_id)

        if not user:
            raise NotFoundException(message="User not found")

        return user

    def get_list(self) -> list[User]:
        """
        Retrieve a list of all users.

        Returns:
            list[User]: A list of all user objects.
        """
        return self.repo.get_list()

    def _update_user(self, *, user_id: str, payload: BaseModel) -> User:
        """
        Internal method to update a user's data.

        Args:
            user_id (str): The user's ID.
            payload (BaseModel): The update data (can be UserUpdate or AdminUserUpdate).

        Returns:
            User: The updated user object.

        Raises:
            NotFoundException: If the user does not exist.
        """
        user = self.repo.get_by_user_id(user_id)

        if not user:
            raise NotFoundException(message="User not found")

        return self.repo.update(user, payload)

    def admin_update(
        self,
        *,
        payload: AdminUserUpdate,
        user_id: str,
        current_user: User,
    ) -> User:
        """
        Update another user's profile information as an admin.

        Args:
            payload (AdminUserUpdate): The admin user's update data.
            user_id (str): The target user's ID.
            current_user (User): The currently authenticated admin user.

        Returns:
            User: The updated user object.

        Raises:
            AppError: If the current user is not an admin.
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
        """
        Update the current user's own profile information.

        Args:
            payload (UserUpdate): The user's update data.
            user_id (str): The target user's ID.
            current_user (User): The currently authenticated user.

        Returns:
            User: The updated user object.

        Raises:
            AppError: If the current user does not have permission to update this user.
        """
        check_permission(current_user=current_user, owner_id=user_id)

        return self._update_user(user_id=user_id, payload=payload)

from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    BadRequestError,
    ForbiddenError,
    NotFoundError,
)
from app.decorators.permissions import check_permission
from app.modules.users.models import User, UserRole
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import (
    AdminUserUpdate,
    UserCreate,
    UserUpdate,
)
from app.utils.helpers import apply_partial_update
from app.utils.pagination import PaginationInfo


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
            User: The created or already-existing user.

        Raises:
            AppError: If attempting to create a duplicate user.
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
            raise BadRequestError(message="User already exists")

    def get_by_id(self, user_id: str) -> User:
        """
        Retrieve a user by their ID.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            User: The user object if found.

        Raises:
            NotFoundException: If no such user exists.
        """
        user = self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found")

        return user

    def list(self, limit: int, offset: int) -> tuple[PaginationInfo, list[User]]:
        """
        List users with pagination support.

        Args:
            limit (int): Maximum users to return.
            offset (int): Number of records to skip.

        Returns:
            tuple[PaginationInfo, list[User]]: Pagination metadata and user list.
        """

        return self.repo.list(limit, offset)

    def _partial_update_user(self, *, user_id: str, payload: BaseModel) -> User:
        """
        Internal helper to partially update user fields.

        Args:
            user_id (str): The ID of the user to update.
            payload (BaseModel): Update payload (UserUpdate or AdminUserUpdate).

        Returns:
            User: Updated user object.

        Raises:
            NotFoundException: If the user is not found.
        """
        user = self.repo.get_by_id(user_id)

        if not user:
            raise NotFoundError(message="User not found")

        apply_partial_update(instance=user, data=payload.model_dump(exclude_unset=True))

        return self.repo.partial_update(user)

    def admin_partial_update(
        self,
        *,
        payload: AdminUserUpdate,
        user_id: str,
        current_user: User,
    ) -> User:
        """
        Partially update another user's profile as an admin.

        Only admins may use this operation.

        Args:
            payload (AdminUserUpdate): Fields to update (admin-level).
            user_id (str): Target user ID.
            current_user (User): Authenticated admin user.

        Returns:
            User: Updated user object.

        Raises:
            AppError: If current user is not an admin.
        """
        if current_user.role != UserRole.ADMIN:
            raise ForbiddenError(message="Permission denied")

        return self._partial_update_user(user_id=user_id, payload=payload)

    def partial_update(
        self,
        *,
        payload: UserUpdate,
        user_id: str,
        current_user: User,
    ) -> User:
        """
        Partially update a user's own profile.

        Users may only update their own record. Ownership validation is enforced
        by check_permission.

        Args:
            payload (UserUpdate): Fields to update.
            user_id (str): The user record to modify.
            current_user (User): Authenticated user attempting the update.

        Returns:
            User: Updated user object.

        Raises:
            AppError: If the user does not have permission to update this record.
        """
        check_permission(current_user=current_user, owner_id=user_id)

        return self._partial_update_user(user_id=user_id, payload=payload)

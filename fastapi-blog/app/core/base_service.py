from typing import Any

from app.core.constants import UserRole
from app.core.exceptions import ForbiddenError
from app.modules.users.models import User


class BaseService:
    def _check_is_admin_or_owner(
        self,
        current_user: User,
        *,
        owner_id: Any | None = None,
    ) -> None:
        """
        Internal permission check for admin/owner logic.

        Args:
            current_user (User): The user attempting the action.
            owner_id (Any | None, optional): ID of the resource owner for ownership check.

        Raises:
            ForbiddenError: If the user is neither admin nor the owner (when owner_id provided).
        """
        # Admin → full access
        if current_user.role == UserRole.ADMIN:
            return

        # Owner → allowed
        if owner_id is not None and current_user.id == owner_id:
            return

        raise ForbiddenError(message="Permission denied")

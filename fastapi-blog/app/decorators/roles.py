from __future__ import annotations

from collections.abc import Callable

from fastapi import Depends

from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.dependencies.auth import get_current_active_user
from app.modules.users.model import User, UserRole


def require_roles(*allowed_roles: UserRole) -> Callable[[User], User]:
    """
    RBAC dependency factory.

    Usage:
        current_user = Depends(require_roles(UserRole.admin))
    """

    def dependency(current_user: User = Depends(get_current_active_user)) -> User:
        user_role = (
            UserRole(current_user.role)
            if isinstance(current_user.role, str)
            else current_user.role
        )

        if user_role not in allowed_roles:
            raise AppError(
                code=ErrorCode.forbidden,
                message="Permission denied",
                status_code=StatusCode.forbidden,
            )

        return current_user

    return dependency

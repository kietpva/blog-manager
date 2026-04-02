from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.modules.users.models import UserRole


def check_permission(current_user, owner_id):
    """
    Check if the current user has permission to perform an action on a resource.

    Admin users have full permissions. Regular users can only access or modify resources they own.

    Args:
        current_user: The user attempting to perform the action.
    """

    # Admin has full permissions
    if current_user.role == UserRole.ADMIN:
        return True

    # Users can only access their own posts
    if current_user.id == owner_id:
        return True

    raise AppError(
        code=ErrorCode.FORBIDDEN,
        message="Permission denied",
        status_code=StatusCode.FORBIDDEN,
    )

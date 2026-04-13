import uuid

from fastapi import APIRouter, Depends, Query

from src.app.core.constants import MAX_ITEMS_PER_PAGE, SortOrder
from src.app.dependencies.rbac import Admin, Authenticated
from src.app.modules.users.dependencies import get_user_service
from src.app.modules.users.models import User
from src.app.modules.users.schemas import (
    UserRead,
    UserUpdate,
)
from src.app.modules.users.services import UserService
from src.app.utils.pagination import (
    Meta,
    PaginationResponse,
    ResponseData,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}",
    dependencies=[Authenticated],
    response_model=ResponseData[UserRead],
)
def get_by_id(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    """
    Retrieve a user's details by user ID.

    This endpoint fetches and returns information about a specific user. The
    endpoint requires authentication. If the authenticated user is not an admin,
    they may only access their own information.

    Args:
        user_id (uuid.UUID): The UUID of the user to retrieve.
        service (UserService): Dependency injected user service.

    Returns:
        ResponseData[UserRead]: The user information, wrapped in a standard response model.
    """
    data = service.get_by_id(user_id)
    return ResponseData[UserRead](data=data)


@router.get(
    "",
    dependencies=[Admin],
    response_model=PaginationResponse[list[UserRead]],
)
def users(
    limit: int = Query(10, ge=1, le=MAX_ITEMS_PER_PAGE),
    offset: int = Query(0, ge=0),
    order_by: SortOrder = SortOrder.NEWEST,
    search: str | None = None,
    service: UserService = Depends(get_user_service),
):
    """
    Retrieve a paginated list of all users (admin only).

    This endpoint is restricted to admin users and returns users in a paginated format.

    Args:
        limit (int): Maximum number of users to return.
        offset (int): Number of records to skip.
        service (UserService): Dependency injected user service.

    Returns:
        PaginationResponse[List[UserRead]]: Paginated user list and metadata.
    """
    pagination, items = service.list(
        limit=limit, offset=offset, order_by=order_by, search=search
    )
    return PaginationResponse[list[UserRead]](
        data=items,
        meta=Meta(pagination=pagination),
    )


@router.patch(
    "/{user_id}",
    dependencies=[Authenticated],
    response_model=ResponseData[UserRead],
)
def partial_update(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
    me: User = Authenticated,
):
    """
    Update the profile details of the currently authenticated user.

    Allows a user to update their own account information. Authorization is required.
    Non-admin users can only update their own user record.

    Args:
        user_id (uuid.UUID): The UUID of the user to update (must match authenticated user).
        user_update (UserUpdate): Partial update payload.
        service (UserService): Dependency injected user service.
        me (User): The currently authenticated user.

    Returns:
        ResponseData[UserRead]: The updated user data.
    """
    data = service.partial_update(payload=user_update, user_id=user_id, current_user=me)
    return ResponseData[UserRead](data=data)

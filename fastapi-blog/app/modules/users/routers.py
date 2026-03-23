from typing import List
import uuid
from fastapi import APIRouter, Depends
from app.dependencies.rbac import Admin, Authenticated
from app.dependencies.users import get_user_service
from app.modules.users.models import User
from app.modules.users.schemas import (
    AdminUserRead,
    AdminUserUpdate,
    UserRead,
    UserUpdate,
)
from app.modules.users.services import UserService
from app.core.constants import ResponseData

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/{user_id}", dependencies=[Authenticated], response_model=ResponseData[UserRead]
)
def get_user(
    user_id: uuid.UUID,
    service: UserService = Depends(get_user_service),
):
    """
    Retrieve the currently authenticated user's information
    """
    user = service.get_user(user_id)
    return ResponseData[UserRead](data=user)


@router.get("", dependencies=[Admin], response_model=ResponseData[List[UserRead]])
def get_users(
    service: UserService = Depends(get_user_service),
):
    """
    Retrieve a list of all users (Admin only)
    """
    users = service.get_list()
    return ResponseData[List[UserRead]](data=users)


@router.patch(
    "/{user_id}",
    dependencies=[Authenticated],
    response_model=ResponseData[UserRead],
)
def update(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    service: UserService = Depends(get_user_service),
    me: User = Authenticated,
):
    """
    Update the current authenticated user's profile information
    """
    result = service.update(payload=user_update, user_id=user_id, current_user=me)
    return ResponseData[UserRead](data=result)


@router.patch(
    "/admin/{user_id}",
    dependencies=[Admin],
    response_model=ResponseData[AdminUserRead],
)
def admin_update(
    user_id: uuid.UUID,
    user_update: AdminUserUpdate,
    service: UserService = Depends(get_user_service),
    me: User = Authenticated,
):
    """
    Update another user's profile as an admin
    """
    result = service.admin_update(payload=user_update, user_id=user_id, current_user=me)
    return ResponseData[AdminUserRead](data=result)

from uuid import UUID

from fastapi import APIRouter, Depends, status

from src.app.dependencies.rbac import Authenticated
from src.app.modules.follows.dependencies import get_follow_service
from src.app.modules.follows.services import FollowService
from src.app.modules.users.models import User

router = APIRouter(prefix="/follows", tags=["Follows"])


@router.post(
    "/{user_id}",
    dependencies=[Authenticated],
    status_code=status.HTTP_204_NO_CONTENT,
)
def follow_user(
    user_id: UUID,
    service: FollowService = Depends(get_follow_service),
    me: User = Authenticated,
):
    return service.create(follower_id=me.id, following_id=user_id)

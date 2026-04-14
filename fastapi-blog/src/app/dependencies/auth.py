from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.app.core.exceptions import (
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
)
from src.app.db.session import SessionLocal
from src.app.modules.users.models import User

security = HTTPBearer()


def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    clerk_id: str | None = getattr(request.state, "clerk_id", None)

    if not clerk_id:
        raise UnauthorizedError(message="Not authenticated")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.auth_id == clerk_id).first()
    finally:
        db.close()

    if not user:
        raise NotFoundError(message="User does not exist")

    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise ForbiddenError(message="Inactive user")
    return user

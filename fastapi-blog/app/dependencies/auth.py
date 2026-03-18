from typing import Optional
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.db.session import SessionLocal
from app.modules.users.model import User

security = HTTPBearer()


def get_current_user(
    request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    clerk_id: Optional[str] = getattr(request.state, "clerk_id", None)

    if not clerk_id:
        raise AppError(
            code=ErrorCode.unauthorized,
            message="Not authenticated",
            status_code=StatusCode.unauthorized,
        )

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.auth_id == clerk_id).first()
    finally:
        db.close()

    if not user:
        raise AppError(
            code=ErrorCode.user_not_found,
            message="User does not exist",
            status_code=StatusCode.unauthorized,
        )

    return user


def get_current_active_user(user: User = Depends(get_current_user)) -> User:
    if not user.is_active:
        raise AppError(
            code=ErrorCode.forbidden,
            message="Inactive user",
            status_code=StatusCode.forbidden,
        )
    return user

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.jwt import verify_clerk_token

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Dependency to retrieve and verify the current authenticated user using a JWT token
    provided in the Authorization header.
    """
    token = credentials.credentials
    return verify_clerk_token(token)

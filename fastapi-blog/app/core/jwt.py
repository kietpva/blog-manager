# Handles authentication logic such as verifying JWT tokens
# and extracting user information from tokens
import httpx
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings
from app.core.exceptions import AppError, ErrorCode, StatusCode

security = HTTPBearer()

_jwks_cache: dict | None = None


def get_jwks() -> dict:
    """
    Retrieve the JSON Web Key Set (JWKS) used to verify JWT tokens.

    This function fetches the JWKS from the Clerk service and caches it
    for future use. If the JWKS is already cached, the cached version
    will be returned.
    """
    global _jwks_cache

    if _jwks_cache:
        return _jwks_cache

    try:
        res = httpx.get(settings.CLERK_JWKS_URL, timeout=5.0)
        res.raise_for_status()
        _jwks_cache = res.json()
        return _jwks_cache

    except Exception:
        raise AppError(
            code=ErrorCode.SERVICE_UNAVAILABLE,
            message="Unable to fetch JWKS",
            status_code=StatusCode.SERVICE_UNAVAILABLE,
        )


def get_public_key(token: str) -> dict:
    """
    Extract and return the public key from the JWKS corresponding to the given JWT token.
    """
    try:
        header = jwt.get_unverified_header(token)
    except JWTError:
        raise AppError(
            code=ErrorCode.UNAUTHORIZED,
            message="Invalid token header",
            status_code=StatusCode.UNAUTHORIZED,
        )

    kid = header.get("kid")

    if not kid:
        raise AppError(
            code=ErrorCode.UNAUTHORIZED,
            message="Token missing kid",
            status_code=StatusCode.UNAUTHORIZED,
        )

    jwks = get_jwks()

    for key in jwks["keys"]:
        if key["kid"] == kid:
            return key
    raise AppError(
        code=ErrorCode.UNAUTHORIZED,
        message="Public key not found",
        status_code=StatusCode.UNAUTHORIZED,
    )


def verify_auth_token(token: str) -> dict:
    """
    Verify the provided Clerk JWT token and return its payload.
    """
    try:
        key = get_public_key(token)

        payload = jwt.decode(
            token,
            key,
            algorithms=["RS256"],
            issuer=settings.CLERK_ISSUER,
            options={"verify_aud": False},
        )

        return payload

    except JWTError:
        raise AppError(
            code=ErrorCode.UNAUTHORIZED,
            message="Invalid or expired token",
            status_code=StatusCode.UNAUTHORIZED,
        )

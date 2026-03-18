from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from app.core.jwt import verify_clerk_token
from app.core.exceptions import (
    AppError,
    ErrorCode,
    StatusCode,
    as_error_response,
    http_exception_to_error,
)
from app.db.session import SessionLocal
from app.modules.users.model import User


def register_middleware(app: FastAPI) -> None:
    """
    Register authentication middleware to the FastAPI application.

    This function adds the custom AuthMiddleware to the provided FastAPI app,
    enabling JWT-based authentication for incoming requests.
    """
    app.add_middleware(AuthMiddleware)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling JWT authentication in incoming requests.

    This middleware checks for the presence of a valid "Authorization: Bearer <token>"
    header in each request. If present, it verifies the token and attaches the decoded
    user payload to the request state. Otherwise, or if verification fails, it returns
    an appropriate error response.
    """

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")

        try:
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                payload = verify_clerk_token(token)
                clerk_id = payload.get("sub") or payload.get("user_id")

                if not clerk_id:
                    raise AppError(
                        code=ErrorCode.UNAUTHORIZED,
                        message="Token missing user id",
                        status_code=StatusCode.UNAUTHORIZED,
                    )

                db = SessionLocal()
                try:
                    user = db.query(User).filter(User.auth_id == clerk_id).first()
                finally:
                    db.close()

                if not user:
                    raise AppError(
                        code=ErrorCode.USER_NOT_FOUND,
                        message="User does not exist",
                        status_code=StatusCode.UNAUTHORIZED,
                    )

                # Second level authorization: attach DB user for cross-layer use
                request.state.user = user
                request.state.auth = payload
        except AppError as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content=as_error_response(code=exc.code, message=exc.message),
            )
        except HTTPException as exc:
            status_code, content = http_exception_to_error(exc)
            return JSONResponse(status_code=status_code, content=content)

        response = await call_next(request)
        return response

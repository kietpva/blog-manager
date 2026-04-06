import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    AppError,
    ErrorCode,
    StatusCode,
    UnauthorizedError,
    as_error_response,
)
from app.core.jwt import verify_auth_token
from app.db.session import SessionLocal
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import UserCreate
from app.modules.users.services import UserService


def register_auth_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        request_id = getattr(request.state, "request_id", None)

        try:
            if auth_header:
                parts = auth_header.split(" ")

                if len(parts) != 2 or parts[0] != "Bearer":
                    raise UnauthorizedError(
                        message="Invalid authorization header format"
                    )

                token = parts[1]
                payload = verify_auth_token(token)

                auth_id = payload.get("sub") or payload.get("user_id")
                if not auth_id:
                    raise UnauthorizedError(message="Token missing auth id")

                request.state.auth = payload
                request.state.clerk_id = auth_id

                email = payload.get("email")
                if not email:
                    raise UnauthorizedError(message="Email missing from token")

                first_name = payload.get("first_name") or ""
                last_name = payload.get("last_name") or ""

                user_data = UserCreate(
                    auth_id=auth_id,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                )

                db = SessionLocal()
                try:
                    repo = UserRepository(db)
                    service = UserService(repo)
                    user = service.create(user_data)
                    db.expunge(user)
                    request.state.current_user = user
                finally:
                    db.close()

        except AppError as exc:
            logging.warning(
                "auth_failed",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "path": request.url.path,
                        "message": exc.message,
                    }
                },
            )

            return JSONResponse(
                status_code=exc.status_code,
                content=as_error_response(code=exc.code, message=exc.message),
            )

        except Exception:
            logging.exception(
                "auth_error",
                extra={
                    "extra_data": {
                        "request_id": request_id,
                        "path": request.url.path,
                    }
                },
            )

            return JSONResponse(
                status_code=StatusCode.UNAUTHORIZED,
                content=as_error_response(
                    code=ErrorCode.UNAUTHORIZED,
                    message="Authentication failed",
                ),
            )

        return await call_next(request)

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.jwt import verify_clerk_token
from app.core.exceptions import (
    AppError,
    ErrorCode,
    StatusCode,
    as_error_response,
)


def register_auth_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        request_id = getattr(request.state, "request_id", None)

        try:
            if auth_header:
                parts = auth_header.split(" ")

                if len(parts) != 2 or parts[0] != "Bearer":
                    raise AppError(
                        code=ErrorCode.unauthorized,
                        message="Invalid authorization header format",
                        status_code=StatusCode.unauthorized,
                    )

                token = parts[1]
                payload = verify_clerk_token(token)

                clerk_id = payload.get("sub") or payload.get("user_id")
                if not clerk_id:
                    raise AppError(
                        code=ErrorCode.unauthorized,
                        message="Token missing user id",
                        status_code=StatusCode.unauthorized,
                    )

                request.state.auth = payload
                request.state.clerk_id = clerk_id

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
                status_code=StatusCode.unauthorized,
                content=as_error_response(
                    code=ErrorCode.unauthorized,
                    message="Authentication failed",
                ),
            )

        return await call_next(request)

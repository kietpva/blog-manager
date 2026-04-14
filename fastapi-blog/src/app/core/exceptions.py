from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.app.core.constants import ErrorCode, StatusCode


class AppError(Exception):
    status_code: int = StatusCode.BAD_REQUEST
    code: str = ErrorCode.BAD_REQUEST
    message: str = "Application error"

    def __init__(self, message: str | None = None):
        if message:
            self.message = message

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
        }


class BadRequestError(AppError):
    status_code = StatusCode.BAD_REQUEST
    code = ErrorCode.BAD_REQUEST
    message = "Bad request"


class UnauthorizedError(AppError):
    status_code = StatusCode.UNAUTHORIZED
    code = ErrorCode.UNAUTHORIZED
    message = "Unauthorized"


class ForbiddenError(AppError):
    status_code = StatusCode.FORBIDDEN
    code = ErrorCode.FORBIDDEN
    message = "Forbidden"


class NotFoundError(AppError):
    status_code = StatusCode.NOT_FOUND
    code = ErrorCode.NOT_FOUND
    message = "Resource not found"


class InternalServerError(AppError):
    status_code = StatusCode.INTERNAL_SERVER_ERROR
    code = ErrorCode.INTERNAL_SERVER_ERROR
    message = "Internal server error"


class ServiceUnavailableError(AppError):
    status_code = StatusCode.SERVICE_UNAVAILABLE
    code = ErrorCode.SERVICE_UNAVAILABLE
    message = "Service unavailable"


def as_error_response(*, code: str, message: str) -> dict[str, Any]:
    """
    Format an error response dictionary with the specified error code and message.
    """

    return {"error": {"code": code, "message": message}}


def http_exception_to_error(exc: HTTPException) -> tuple[int, dict[str, Any]]:
    """
    Convert an HTTPException to a tuple containing the status code and
    a standardized error response dictionary.
    """

    detail = exc.detail

    if isinstance(detail, dict) and "error" in detail:
        err = detail.get("error")
        if (
            isinstance(err, dict)
            and isinstance(err.get("code"), str)
            and isinstance(err.get("message"), str)
        ):
            return exc.status_code, {
                "error": {"code": err["code"], "message": err["message"]}
            }

    if (
        isinstance(detail, dict)
        and isinstance(detail.get("code"), str)
        and isinstance(detail.get("message"), str)
    ):
        return exc.status_code, as_error_response(
            code=detail["code"], message=detail["message"]
        )

    if isinstance(detail, str) and detail.strip():
        return exc.status_code, as_error_response(code="http_error", message=detail)

    return exc.status_code, as_error_response(
        code="http_error", message="Request failed"
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register custom exception handlers for FastAPI application.
    """

    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content=as_error_response(code=exc.code, message=exc.message),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        status_code, content = http_exception_to_error(exc)
        return JSONResponse(status_code=status_code, content=content)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=as_error_response(code="validation_error", message=str(exc)),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(_: Request, exc: Exception):
        return JSONResponse(
            status_code=StatusCode.INTERNAL_SERVER_ERROR,
            content=as_error_response(
                code=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Internal server error",
            ),
        )

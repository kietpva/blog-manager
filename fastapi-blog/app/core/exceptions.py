from dataclasses import dataclass
from enum import IntEnum, StrEnum
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class StatusCode(IntEnum):
    ok = 200
    created = 201
    no_content = 204
    bad_request = 400
    unauthorized = 401
    forbidden = 403
    not_found = 404
    method_not_allowed = 405
    internal_server_error = 500
    service_unavailable = 503


class ErrorCode(StrEnum):
    bad_request = "bad_request"
    unauthorized = "unauthorized"
    forbidden = "forbidden"
    not_found = "not_found"
    internal_server_error = "internal_server_error"
    service_unavailable = "service_unavailable"

    post_not_found = "post_not_found"
    user_not_found = "user_not_found"
    inactivate_user = "inactivate_user"


@dataclass(slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400


class NotFoundException(AppError):
    """
    Exception raised when a requested resource is not found.
    """

    def __init__(
        self,
        *,
        message: str = "Resource not found",
        code: str = ErrorCode.not_found,
    ):
        super().__init__(
            code=code,
            message=message,
            status_code=StatusCode.not_found,
        )


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
            status_code=StatusCode.internal_server_error,
            content=as_error_response(
                code=ErrorCode.internal_server_error,
                message="Internal server error",
            ),
        )

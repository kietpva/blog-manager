from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


@dataclass(frozen=True, slots=True)
class AppError(Exception):
    code: str
    message: str
    status_code: int = 400


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


class StatusCode:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class ErrorCode:
    BAD_REQUEST = "bad_request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"

    POST_NOT_FOUND = "post_not_found"
    USER_NOT_FOUND = "user_not_found"


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

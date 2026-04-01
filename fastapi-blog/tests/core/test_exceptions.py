from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.core.exceptions import (
    AppError,
    ErrorCode,
    NotFoundException,
    StatusCode,
    as_error_response,
    http_exception_to_error,
    register_exception_handlers,
)


def test_status_code_and_error_code_values():
    """
    Test that StatusCode and ErrorCode values are as expected.

    Ensures StatusCode.ok, StatusCode.service_unavailable, and key ErrorCode attributes
    have the correct values from enums/constants.
    """
    assert StatusCode.ok == 200
    assert StatusCode.service_unavailable == 503

    assert ErrorCode.bad_request == "bad_request"
    assert ErrorCode.internal_server_error == "internal_server_error"
    assert ErrorCode.service_unavailable == "service_unavailable"


def test_not_found_exception_defaults():
    """
    Test the default construction of a NotFoundException.

    Asserts that it subclasses AppError and checks the default code, message, and status.
    """
    exc = NotFoundException()
    assert isinstance(exc, AppError)
    assert exc.code == ErrorCode.not_found
    assert exc.message == "Resource not found"
    assert exc.status_code == StatusCode.not_found


def test_not_found_exception_custom_message_and_code():
    """
    Test NotFoundException with a custom message and error code.

    Asserts that a custom code and message are properly set on exception instantiation.
    """
    exc = NotFoundException(message="Post not found", code=ErrorCode.post_not_found)
    assert exc.code == ErrorCode.post_not_found
    assert exc.message == "Post not found"
    assert exc.status_code == StatusCode.not_found


def test_as_error_response_builds_expected_shape():
    """
    Test as_error_response utility returns the expected error payload shape.

    Ensures the dict output has the "error" key and values as expected.
    """
    assert as_error_response(code="x", message="y") == {
        "error": {"code": "x", "message": "y"}
    }


@pytest.mark.parametrize(
    "detail, expected",
    [
        (
            {"error": {"code": "c1", "message": "m1"}},
            {"error": {"code": "c1", "message": "m1"}},
        ),
        (
            {"code": "c2", "message": "m2"},
            {"error": {"code": "c2", "message": "m2"}},
        ),
        (
            "simple error",
            {"error": {"code": "http_error", "message": "simple error"}},
        ),
        (
            {},
            {"error": {"code": "http_error", "message": "Request failed"}},
        ),
    ],
)
def test_http_exception_to_error_variants(detail, expected):
    """
    Test http_exception_to_error with different types of detail payloads.

    Parametrized to verify different shapes:
      - already in expected error format,
      - code/message dict,
      - simple string,
      - empty dict.
    Returns correct status_code and error shape in body.
    """
    exc = HTTPException(status_code=418, detail=detail)
    status_code, body = http_exception_to_error(exc)

    assert status_code == 418
    assert body == expected


def test_register_exception_handlers_triggers_custom_handlers():
    """
    Test that registering exception handlers results in custom FastAPI error responses.

    Registers handlers, then creates endpoints that raise:
        - an AppError,
        - a standard HTTPException,
        - a validation error,
        - a global (non-HTTP, e.g., RuntimeError) exception.

    Verifies that responses have correct status codes as per API error handling layering.
    """
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/app-error")
    def raise_app_error():
        raise AppError(
            code=ErrorCode.forbidden,
            message="Permission denied",
            status_code=StatusCode.forbidden,
        )

    @app.get("/http-error")
    def raise_http_error():
        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/validate")
    def validate(q: int):
        return {"q": q}

    @app.get("/global-error")
    def raise_global_error():
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)

    r = client.get("/app-error")
    assert r.status_code == 403

    r = client.get("/http-error")
    assert r.status_code == 404

    r = client.get("/validate?q=abc")
    assert r.status_code == 422

    r = client.get("/global-error")
    assert r.status_code == 500

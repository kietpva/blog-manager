from enum import IntEnum, StrEnum

MAX_ITEMS_PER_PAGE: int = 100


class StatusCode(IntEnum):
    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    INTERNAL_SERVER_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class ErrorCode(StrEnum):
    BAD_REQUEST = "bad_request"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class ClerkEventEnum(StrEnum):
    USER_CREATED = "user.created"

from enum import IntEnum, StrEnum
from typing import NamedTuple
from uuid import UUID

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
    USER_UPDATED = "user.updated"


class SortOrder(StrEnum):
    NEWEST = "newest"
    OLDEST = "oldest"


class NotificationType(StrEnum):
    DAILY_REPORT = "daily_report"
    FOLLOW = "follow"


class NotificationRecipient(NamedTuple):
    user_id: UUID
    ws_user_id: str


class WSEvent(StrEnum):
    NOTIFICATION_CREATED = "notification_created"

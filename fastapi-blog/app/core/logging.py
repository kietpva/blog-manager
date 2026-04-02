import json
import logging
import time
import uuid
from contextvars import ContextVar
from typing import Any

from fastapi import Request

from app.core.config import settings

# ====== Context ======
request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)


# ====== Helpers ======
STANDARD_LOG_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
}


def extract_extra(record: logging.LogRecord) -> dict[str, Any]:
    return {k: v for k, v in record.__dict__.items() if k not in STANDARD_LOG_ATTRS}


# ====== Formatters ======
class JsonFormatter(logging.Formatter):
    """
    Formats log records as JSON objects.
    """

    def format(self, record: logging.LogRecord) -> str:
        log = {
            "level": record.levelname,
            "message": record.getMessage(),
            "time": self.formatTime(record),
            "request_id": request_id_ctx.get(),
        }

        log.update(extract_extra(record))

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, separators=(",", ":"))


class PrettyFormatter(logging.Formatter):
    """
    Formats log records as pretty-printed strings.
    """

    def format(self, record: logging.LogRecord) -> str:
        base = f"[{record.levelname}] {self.formatTime(record)} - {record.getMessage()}"

        request_id = request_id_ctx.get()
        if request_id:
            base += f" | request_id={request_id}"

        extra = extract_extra(record)
        if extra:
            extra_str = " ".join(f"{k}={v}" for k, v in extra.items())
            base = f"{base} | {extra_str}"

        if record.exc_info:
            base += f"\n{self.formatException(record.exc_info)}"

        return base


# ====== Setup ======
def setup_logging():
    """
    Sets up logging for the application.
    """
    logger = logging.getLogger()

    if logger.handlers:
        return  # avoid adding duplicate handler

    handler = logging.StreamHandler()

    formatter = PrettyFormatter() if settings.DEBUG else JsonFormatter()
    handler.setFormatter(formatter)

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    # reduce log noise from sqlalchemy
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


# ====== Middleware ======
async def logging_middleware(request: Request, call_next):
    """
    Logs the request and response.
    """
    request_id = str(uuid.uuid4())
    request_id_ctx.set(request_id)

    start = time.time()

    try:
        response = await call_next(request)
    except Exception:
        duration = (time.time() - start) * 1000

        logging.exception(
            "request_failed",
            extra={
                "request_id": request_id,
                "path": request.url.path,
                "method": request.method,
                "duration_ms": round(duration, 2),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )
        raise

    duration = (time.time() - start) * 1000

    logging.info(
        "request_completed",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "status_code": response.status_code,
            "duration_ms": round(duration, 2),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        },
    )

    return response

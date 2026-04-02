import logging
import time
import uuid

from fastapi import Request
from fastapi.responses import Response


async def logging_middleware(request: Request, call_next) -> Response:
    """
    Logs the request and response.
    """
    request_id = str(uuid.uuid4())
    start = time.time()

    # attach to request to be used by other middleware
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        status_code = response.status_code

    except Exception:
        duration = (time.time() - start) * 1000

        logging.exception(
            "request_failed",
            extra={
                "extra_data": {
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration, 2),
                }
            },
        )
        raise

    duration = (time.time() - start) * 1000

    logging.info(
        "request_completed",
        extra={
            "extra_data": {
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "duration_ms": round(duration, 2),
            }
        },
    )

    return response

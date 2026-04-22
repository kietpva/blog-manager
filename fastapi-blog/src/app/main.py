from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.app.core.config import settings
from src.app.core.exceptions import register_exception_handlers
from src.app.core.logging import logging_middleware, setup_logging
from src.app.core.middleware.auth_middleware import register_auth_middleware
from src.app.core.scheduler import start_scheduler, stop_scheduler
from src.app.db.init_db import init_db
from src.app.routers import register_routers_api_v1


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles application startup and shutdown events such as database initialization,
    scheduler startup/shutdown, and (in debug mode) ngrok public URL exposure.
    """
    init_db()
    if settings.DEBUG:
        """
        If the application is running in DEBUG mode,
        expose a public URL using ngrok for easier testing and development.
        """

        import logging

        from pyngrok import ngrok

        public_url = ngrok.connect(8000, bind_tls=True).public_url
        logging.info(f"Public URL: {public_url}")
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="FastAPI Blog",
    description="Practice project using FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

# Setup logging
setup_logging()


@app.middleware("http")
async def log_requests(request, call_next):
    return await logging_middleware(request, call_next)


# Middleware
register_auth_middleware(app)
# register_middleware(app)

# Routers
register_routers_api_v1(app)

# Exception handlers
register_exception_handlers(app)

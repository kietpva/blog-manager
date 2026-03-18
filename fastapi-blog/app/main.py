from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.exceptions import register_exception_handlers
from app.db.init_db import init_db
from app.middleware.auth_middleware import register_middleware
from app.routers import register_routers


def create_app() -> FastAPI:
    """
    Create and configure FastAPI application
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        init_db()

        yield

    app = FastAPI(
        title="FastAPI Blog",
        description="Practice project using FastAPI",
        version="1.0.0",
    )

    # Middleware
    register_middleware(app)

    # Routers
    register_routers(app)

    # Exception handlers
    register_exception_handlers(app)

    return app


app = create_app()

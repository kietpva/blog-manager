from fastapi import FastAPI

from app.modules.health.routers import router as health_router
from app.modules.users.routers import router as user_router
from app.modules.auth.routers import router as auth_router


def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(health_router)

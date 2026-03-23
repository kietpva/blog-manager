from fastapi import FastAPI

from app.modules.health.routers import router as health_router
from app.modules.users.routers import router as users_router
from app.modules.auth.routers import router as auth_router
from app.modules.posts.routers import router as posts_router


def register_routers(app: FastAPI) -> None:
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(posts_router)
    app.include_router(health_router)

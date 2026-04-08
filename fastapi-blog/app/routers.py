from fastapi import FastAPI

from app.apis.v1.routers import router as v1_router
from app.modules.health.routers import router as health_router
from app.modules.webhooks.routers import router as webhooks_router


def register_routers_api_v1(app: FastAPI) -> None:

    # version v1
    app.include_router(v1_router)

    app.include_router(webhooks_router)
    app.include_router(health_router)

from fastapi import APIRouter

from src.app.modules.categories.routers import router as categories_router
from src.app.modules.follows.routers import router as follows_router
from src.app.modules.notifications.routers import router as notifications_router
from src.app.modules.notifications.ws import router as ws_router
from src.app.modules.posts.routers import router as posts_router
from src.app.modules.users.routers import router as users_router

router = APIRouter(prefix="/api/v1")

# include all modules into v1
router.include_router(users_router)
router.include_router(posts_router)
router.include_router(categories_router)
router.include_router(notifications_router)
router.include_router(follows_router)
router.include_router(ws_router)

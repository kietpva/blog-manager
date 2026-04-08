from fastapi import APIRouter

from app.modules.categories.routers import router as categories_router
from app.modules.posts.routers import router as posts_router
from app.modules.users.routers import router as users_router

router = APIRouter(prefix="/api/v1")

# include all modules into v1
router.include_router(users_router)
router.include_router(posts_router)
router.include_router(categories_router)

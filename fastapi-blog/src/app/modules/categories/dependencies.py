from fastapi import Depends
from sqlalchemy.orm import Session

from src.app.core.dependencies import get_db
from src.app.modules.categories.repositories import CategoryRepository
from src.app.modules.categories.services import CategoryService


def get_category_repository(
    db: Session = Depends(get_db),
) -> CategoryRepository:
    """
    Dependency to provide a CategoryRepository instance.

    Args:
        db (Session): Database session from dependency injection.

    Returns:
        CategoryRepository: Repository instance.
    """
    return CategoryRepository(db)


def get_category_service(
    repo: CategoryRepository = Depends(get_category_repository),
) -> CategoryService:
    """
    Dependency to provide a CategoryService instance.

    Args:
        repo (CategoryRepository): Repository instance.

    Returns:
        CategoryService: Service instance.
    """
    return CategoryService(repo)

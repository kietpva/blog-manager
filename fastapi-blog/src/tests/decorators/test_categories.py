from __future__ import annotations

from unittest.mock import Mock

from src.app.modules.categories.dependencies import (
    get_category_repository,
    get_category_service,
)
from src.app.modules.categories.repositories import CategoryRepository
from src.app.modules.categories.services import CategoryService


def test_get_category_repository_returns_repository_instance():
    """
    Test that get_category_repository returns an instance of CategoryRepository
    and that it stores the provided db instance on its .db attribute.
    """

    db = Mock()

    repo = get_category_repository(db)

    assert isinstance(repo, CategoryRepository)
    assert repo.db is db  # relies on repository storing db on .db


def test_get_category_service_returns_service_instance():
    """
    Test that get_category_service returns an instance of CategoryService
    when provided with a repository.
    """

    repo = Mock()

    service = get_category_service(repo)

    assert isinstance(service, CategoryService)

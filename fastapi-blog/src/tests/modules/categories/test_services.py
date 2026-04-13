from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.app.core.exceptions import AppError, ErrorCode, NotFoundError, StatusCode
from src.app.modules.categories.models import Category
from src.app.modules.categories.repositories import CategoryRepository
from src.app.modules.categories.schemas import CategoryCreate, CategoryUpdate
from src.app.modules.categories.services import CategoryService


@pytest.fixture
def repo() -> Mock:
    """Fixture that returns a mocked CategoryRepository."""
    return Mock(spec=CategoryRepository)


@pytest.fixture
def service(repo: Mock) -> CategoryService:
    """Fixture that returns a CategoryService using the mocked repository."""
    return CategoryService(repo)


def make_category(
    *,
    category_id=None,
    name: str = "tech",
    description: str = "Technology",
) -> Category:
    """
    Utility function to create a Category instance with the given parameters.

    Args:
        category_id: Optional ID to assign to the category.
        name: Name of the category.
        description: Description of the category.

    Returns:
        Category instance.
    """
    category = Category(name=name, description=description)
    category.id = category_id or uuid4()
    return category


def test_create_raises_bad_request_when_name_exists(
    service: CategoryService, repo: Mock
):
    """
    Test that creating a category with a duplicate name raises an AppError with proper status.
    The repository's create method should not be called.
    """
    existing = make_category(name="tech")
    repo.get_by_name.return_value = existing

    payload = CategoryCreate(name="tech", description="desc")

    with pytest.raises(AppError) as exc_info:
        service.create(payload)

    assert exc_info.value.code == ErrorCode.BAD_REQUEST
    assert exc_info.value.message == "Category name already exists"
    assert exc_info.value.status_code == StatusCode.BAD_REQUEST
    repo.create.assert_not_called()


def test_create_calls_repo_create_with_new_category(
    service: CategoryService, repo: Mock
):
    """
    Test that creating a category with a unique name calls the repo's create method
    with the correct data and returns the new category.
    """
    repo.get_by_name.return_value = None
    repo.create.side_effect = lambda category: category

    payload = CategoryCreate(name="python", description="Python posts")
    result = service.create(payload)

    assert result.name == payload.name
    assert result.description == payload.description
    repo.get_by_name.assert_called_once_with(payload.name)
    repo.create.assert_called_once()


def test_list_delegates_to_repository(service: CategoryService, repo: Mock):
    """
    Test that listing categories delegates to the repository and returns the expected result.
    """
    expected = [make_category()]
    repo.list.return_value = expected

    result = service.list()

    assert result == expected
    repo.list.assert_called_once_with()


def test_get_by_id_raises_not_found_when_missing(service: CategoryService, repo: Mock):
    """
    Test that attempting to get a category by a missing ID raises NotFoundException.
    """
    repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        service.get_by_id("missing-id")

    assert exc_info.value.message == "Category not found"
    repo.get_by_id.assert_called_once_with("missing-id")


def test_get_by_id_returns_category_when_found(service: CategoryService, repo: Mock):
    """
    Test that getting a category by a valid ID returns the category instance.
    """
    category = make_category()
    repo.get_by_id.return_value = category

    result = service.get_by_id(category.id)

    assert result is category
    repo.get_by_id.assert_called_once_with(category.id)


def test_partial_update_raises_conflict_when_name_belongs_to_other_category(
    service: CategoryService, repo: Mock
):
    """
    Test that updating a category using a name that already belongs to another category
    raises an AppError for name conflict.
    """
    category = make_category(category_id=uuid4(), name="tech")
    duplicate = make_category(category_id=uuid4(), name="python")
    repo.get_by_id.return_value = category
    repo.get_by_name.return_value = duplicate

    payload = CategoryUpdate(name="python", description="updated")

    with pytest.raises(AppError) as exc_info:
        service.partial_update(str(category.id), payload)

    assert exc_info.value.code == ErrorCode.BAD_REQUEST
    assert exc_info.value.message == "Category name already exists"
    assert exc_info.value.status_code == StatusCode.BAD_REQUEST
    repo.partial_update.assert_not_called()


def test_partial_update_applies_data_and_calls_repo_update(
    service: CategoryService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that updating a category applies the payload via apply_partial_update and persists via repo
    Allows reuse of the same name if IDs match.
    """
    category = make_category(name="old", description="old desc")
    # Same category name lookup is allowed when IDs match.
    repo.get_by_id.return_value = category
    repo.get_by_name.return_value = category
    repo.partial_update.return_value = category

    apply_partial_update_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.categories.services.apply_partial_update",
        apply_partial_update_mock,
    )

    payload = CategoryUpdate(name="new", description="new desc")
    result = service.partial_update(str(category.id), payload)

    apply_partial_update_mock.assert_called_once_with(
        instance=category,
        data=payload.model_dump(exclude_unset=True),
    )
    repo.partial_update.assert_called_once_with(category)
    assert result is category


def test_delete_category_deletes_existing_category(
    service: CategoryService, repo: Mock
):
    """
    Test that deleting an existing category calls the repository's delete method with
    the correct instance.
    """
    category = make_category()
    repo.get_by_id.return_value = category

    service.delete_category(category.id)

    repo.get_by_id.assert_called_once_with(category.id)
    repo.delete.assert_called_once_with(category)

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppError, ErrorCode, NotFoundException, StatusCode
from app.modules.users.models import User, UserRole
from app.modules.users.repositories import UserRepository
from app.modules.users.schemas import AdminUserUpdate, UserCreate, UserUpdate
from app.modules.users.services import UserService
from app.utils.pagination import PaginationInfo


@pytest.fixture
def repo() -> Mock:
    """
    Pytest fixture that returns a Mock instance of the UserRepository.

    Returns:
        Mock: A mock object with the UserRepository spec.
    """
    return Mock(spec=UserRepository)


@pytest.fixture
def service(repo: Mock) -> UserService:
    """
    Pytest fixture that produces a UserService with the repo dependency injected.

    Args:
        repo (Mock): The mocked UserRepository fixture.

    Returns:
        UserService: A UserService instance using the mocked repository.
    """
    return UserService(repo)


@pytest.fixture
def create_payload() -> UserCreate:
    """
    Pytest fixture that returns a standard UserCreate payload for test purposes.

    Returns:
        UserCreate: A user creation schema object with default test values.
    """
    return UserCreate(
        auth_id="auth_123",
        email="user@example.com",
        first_name="John",
        last_name="Doe",
    )


def make_user(**kwargs) -> User:
    """
    Helper function to construct a User instance for tests with optional overrides.

    Args:
        **kwargs: Optional fields to override defaults:
            - auth_id (str)
            - email (str)
            - first_name (str)
            - last_name (str)
            - role (UserRole)
            - is_active (bool)

    Returns:
        User: A User object with the given or default field values.
    """
    return User(
        auth_id=kwargs.get("auth_id", "auth_123"),
        email=kwargs.get("email", "user@example.com"),
        first_name=kwargs.get("first_name", "John"),
        last_name=kwargs.get("last_name", "Doe"),
        role=kwargs.get("role", UserRole.user),
        is_active=kwargs.get("is_active", True),
    )


def test_create_returns_existing_user(service: UserService, repo: Mock, create_payload: UserCreate):
    """
    Test that the service.create() method returns an existing user and does not call repo.create()
    if the user with the given auth_id already exists.

    Args:
        service (UserService): The UserService instance.
        repo (Mock): Mocked repository.
        create_payload (UserCreate): The user creation payload.
    """
    existing_user = make_user(auth_id=create_payload.auth_id)
    repo.get_by_auth_id.return_value = existing_user

    result = service.create(create_payload)

    assert result is existing_user
    repo.create.assert_not_called()


def test_create_calls_repo_with_new_user(service: UserService, repo: Mock, create_payload: UserCreate):
    """
    Test that the service.create() method creates a new user by calling repo.create()
    when no user with the given auth_id exists.

    Args:
        service (UserService): The UserService instance.
        repo (Mock): Mocked repository.
        create_payload (UserCreate): The user creation payload.
    """
    repo.get_by_auth_id.return_value = None
    repo.create.side_effect = lambda user: user

    result = service.create(create_payload)

    assert result.auth_id == create_payload.auth_id
    assert result.email == create_payload.email
    assert result.first_name == create_payload.first_name
    assert result.last_name == create_payload.last_name
    repo.create.assert_called_once()


def test_create_raises_bad_request_when_integrity_error(
    service: UserService, repo: Mock, create_payload: UserCreate
):
    """
    Test that service.create() raises an AppError with the appropriate code, message, 
    and status_code when the repository layer raises an IntegrityError (e.g., due to a unique constraint violation).

    Args:
        service (UserService): The UserService instance.
        repo (Mock): Mocked repository.
        create_payload (UserCreate): The user creation payload.
    """
    repo.get_by_auth_id.return_value = None
    repo.create.side_effect = IntegrityError("stmt", "params", Exception("db-error"))

    with pytest.raises(AppError) as exc_info:
        service.create(create_payload)

    assert exc_info.value.code == ErrorCode.bad_request
    assert exc_info.value.message == "User already exists"
    assert exc_info.value.status_code == StatusCode.bad_request


def test_get_by_id_raises_not_found_when_missing(service: UserService, repo: Mock):
    """
    Test that service.get_by_id raises NotFoundException when the user is missing.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
    """
    repo.get_by_id.return_value = None

    with pytest.raises(NotFoundException) as exc_info:
        service.get_by_id("missing-id")

    assert exc_info.value.message == "User not found"


def test_get_by_id_returns_user_when_found(service: UserService, repo: Mock):
    """
    Test that service.get_by_id returns the user when the user is found.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
    """
    user = make_user(auth_id="auth_found")
    repo.get_by_id.return_value = user

    result = service.get_by_id("user-id")

    assert result is user
    repo.get_by_id.assert_called_once_with("user-id")


def test_list_returns_pagination_and_items(service: UserService, repo: Mock):
    """
    Test that service.list returns both pagination info and items from the repository.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
    """
    page = PaginationInfo(total=1, limit=10, offset=0, hasNext=False, hasPrev=False)
    items = [make_user()]
    repo.list.return_value = (page, items)

    result_page, result_items = service.list(limit=10, offset=0)

    assert result_page is page
    assert result_items == items
    repo.list.assert_called_once_with(10, 0)


def test_partial_update_calls_check_permission_and_repo_update(
    service: UserService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that service.partial_update calls check_permission, applies the update,
    and calls the repository's partial_update method.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch for patching dependencies.
    """
    current_user = SimpleNamespace(id="owner-id", role=UserRole.user)
    target_user = make_user(auth_id="auth_target")
    repo.get_by_id.return_value = target_user
    repo.partial_update.return_value = target_user
    payload = UserUpdate(first_name="Updated")

    check_permission_mock = Mock(return_value=True)
    apply_partial_update_mock = Mock(return_value=None)
    monkeypatch.setattr("app.modules.users.services.check_permission", check_permission_mock)
    monkeypatch.setattr(
        "app.modules.users.services.apply_partial_update", apply_partial_update_mock
    )

    result = service.partial_update(
        payload=payload, user_id="owner-id", current_user=current_user
    )

    assert result is target_user
    check_permission_mock.assert_called_once_with(
        current_user=current_user,
        owner_id="owner-id",
    )
    apply_partial_update_mock.assert_called_once_with(
        instance=target_user,
        data=payload.model_dump(exclude_unset=True),
    )
    repo.partial_update.assert_called_once_with(target_user)


def test_partial_update_raises_not_found_when_target_missing(
    service: UserService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that service.partial_update raises NotFoundException if the target user does not exist.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch for patching dependencies.
    """
    current_user = SimpleNamespace(id="owner-id", role=UserRole.user)
    repo.get_by_id.return_value = None

    check_permission_mock = Mock(return_value=True)
    monkeypatch.setattr("app.modules.users.services.check_permission", check_permission_mock)

    with pytest.raises(NotFoundException) as exc_info:
        service.partial_update(
            payload=UserUpdate(first_name="Updated"),
            user_id="owner-id",
            current_user=current_user,
        )

    assert exc_info.value.message == "User not found"
    repo.partial_update.assert_not_called()


def test_admin_partial_update_denies_non_admin(service: UserService, repo: Mock):
    """
    Test that service.admin_partial_update raises AppError when a non-admin attempts to update another user.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
    """
    current_user = SimpleNamespace(id="user-id", role=UserRole.user)

    with pytest.raises(AppError) as exc_info:
        service.admin_partial_update(
            payload=AdminUserUpdate(role=UserRole.admin),
            user_id="target-id",
            current_user=current_user,
        )

    assert exc_info.value.code == ErrorCode.forbidden
    assert exc_info.value.message == "Permission denied"
    assert exc_info.value.status_code == StatusCode.forbidden
    repo.get_by_id.assert_not_called()


def test_admin_partial_update_updates_target_for_admin(
    service: UserService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that service.admin_partial_update allows admin users to update a target user
    and calls the apply_partial_update and repository's partial_update.

    Args:
        service (UserService): The UserService under test.
        repo (Mock): The mocked user repository.
        monkeypatch (pytest.MonkeyPatch): Pytest monkeypatch for patching dependencies.
    """
    current_user = SimpleNamespace(id="admin-id", role=UserRole.admin)
    target_user = make_user(auth_id="auth_target")
    repo.get_by_id.return_value = target_user
    repo.partial_update.return_value = target_user
    payload = AdminUserUpdate(role=UserRole.admin, is_active=True)
    apply_partial_update_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "app.modules.users.services.apply_partial_update", apply_partial_update_mock
    )

    result = service.admin_partial_update(
        payload=payload,
        user_id="target-id",
        current_user=current_user,
    )

    assert result is target_user
    apply_partial_update_mock.assert_called_once_with(
        instance=target_user,
        data=payload.model_dump(exclude_unset=True),
    )
    repo.partial_update.assert_called_once_with(target_user)

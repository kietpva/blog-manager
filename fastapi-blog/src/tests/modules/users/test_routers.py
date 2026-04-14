from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.app.core.constants import SortOrder
from src.app.core.exceptions import NotFoundError, register_exception_handlers
from src.app.dependencies.rbac import Admin, Authenticated
from src.app.modules.users.dependencies import get_user_service
from src.app.modules.users.models import UserRole
from src.app.modules.users.routers import router
from src.app.utils.pagination import PaginationInfo


def _user_read_obj(user_id):
    """
    Create a SimpleNamespace object representing a user read response.

    Args:
        user_id: The UUID of the user.

    Returns:
        SimpleNamespace: An object with user information.
    """
    return SimpleNamespace(
        id=user_id,
        email="user@example.com",
        first_name="John",
        last_name="Doe",
    )


def _admin_user_read_obj(user_id):
    """
    Create a SimpleNamespace object representing an admin user read response.

    Args:
        user_id: The UUID of the admin user.

    Returns:
        SimpleNamespace: An object with admin user information including role and timestamps.
    """
    return SimpleNamespace(
        id=user_id,
        auth_id="auth_123",
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        role=UserRole.ADMIN,
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


def _build_client(service_mock: Mock) -> tuple[TestClient, SimpleNamespace]:
    """
    Build a FastAPI TestClient with user service and
    authentication dependencies overridden for testing.

    Args:
        service_mock (Mock): A mock object for the user service.

    Returns:
        tuple[TestClient, SimpleNamespace]: A tuple containing a configured TestClient and
        a SimpleNamespace object representing the authenticated admin user.
    """
    app = FastAPI()
    app.include_router(router)
    register_exception_handlers(app)

    me = SimpleNamespace(id=uuid4(), role=UserRole.ADMIN)
    app.dependency_overrides[get_user_service] = lambda: service_mock
    app.dependency_overrides[Authenticated.dependency] = lambda: me
    app.dependency_overrides[Admin.dependency] = lambda: me

    return TestClient(app), me


def test_get_by_id_returns_user():
    """
    Test that the GET /users/{user_id} endpoint returns the expected user data.

    This test verifies that:
      - The endpoint returns a 200 status code when a user exists.
      - The returned user data contains the expected 'id' and 'email' fields.
      - The user service's get_by_id method is called once with the correct user_id.
    """
    service = Mock()
    user_id = uuid4()
    service.get_by_id.return_value = _user_read_obj(user_id)
    client, _ = _build_client(service)

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == str(user_id)
    assert body["data"]["email"] == "user@example.com"
    service.get_by_id.assert_called_once_with(user_id)


def test_get_by_id_returns_404_when_service_raises_not_found():
    """
    Test that GET /users/{user_id} returns 404 when the user service raises NotFoundException.

    This test verifies that:
      - The endpoint returns a 404 status code when the user is not found.
      - The response body contains the correct error code and message.
      - The user service's get_by_id method raises NotFoundException with an appropriate message.
    """
    service = Mock()
    user_id = uuid4()
    service.get_by_id.side_effect = NotFoundError(message="User not found")
    client, _ = _build_client(service)

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "User not found"}
    }


def test_list_returns_paginated_users():
    """
    Test that the GET /users endpoint returns a paginated list of users and
    correct pagination metadata.

    This test verifies that:
      - The endpoint returns a 200 status code.
      - The response contains the expected user data with the correct 'id'.
      - The 'meta.pagination' includes the expected pagination fields and values.
      - The user service's list method is called once with the correct limit and offset values.
    """
    service = Mock()
    user_id = uuid4()
    page = PaginationInfo(total=1, limit=10, offset=0, has_next=False, has_prev=False)
    service.list.return_value = (page, [_user_read_obj(user_id)])
    client, _ = _build_client(service)

    response = client.get("/users?limit=10&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["id"] == str(user_id)
    assert body["meta"]["pagination"]["total"] == 1
    assert body["meta"]["pagination"]["has_next"] is False
    service.list.assert_called_once_with(
        limit=10,
        offset=0,
        order_by=SortOrder.NEWEST,
        search=None,
    )


def test_partial_update_calls_service_and_returns_user():
    """
    Test that PATCH /users/{user_id} calls the service's partial_update method and
    returns the updated user.

    This test verifies that:
      - The endpoint returns a 200 status code.
      - The response body contains the updated user's data
      (but always returns 'John' as first_name in test object).
      - The user service's partial_update method is called once with expected arguments:
          - user_id is passed correctly.
          - current_user context is passed.
          - payload contains only changed fields ("first_name": "Jane") using exclude_unset.
    """
    service = Mock()
    user_id = uuid4()
    service.partial_update.return_value = _user_read_obj(user_id)
    client, me = _build_client(service)

    response = client.patch(
        f"/users/{user_id}",
        json={"first_name": "Jane"},
    )

    assert response.status_code == 200
    assert response.json()["data"]["first_name"] == "John"
    service.partial_update.assert_called_once()
    kwargs = service.partial_update.call_args.kwargs
    assert kwargs["user_id"] == user_id
    assert kwargs["current_user"] is me
    assert kwargs["payload"].model_dump(exclude_unset=True) == {"first_name": "Jane"}

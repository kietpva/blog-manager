from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import NotFoundError, register_exception_handlers
from app.dependencies.categories import get_category_service
from app.dependencies.rbac import Admin, Authenticated
from app.modules.categories.routers import router
from app.modules.users.models import UserRole


def _category_read_obj(category_id, name="tech", description="Technology"):
    """
    Helper function to create a mock category read object with the expected attributes.

    Args:
        category_id: The UUID of the category.
        name: Name of the category.
        description: Description of the category.

    Returns:
        A SimpleNamespace object representing the category.
    """
    return SimpleNamespace(id=category_id, name=name, description=description)


def _build_client(service_mock: Mock) -> tuple[TestClient, SimpleNamespace]:
    """
    Build a FastAPI TestClient with dependency overrides for category service and auth.

    Args:
        service_mock: Mocked service to be injected in the dependency.

    Returns:
        A tuple of (TestClient, SimpleNamespace representing the authed user).
    """
    app = FastAPI()
    app.include_router(router)
    register_exception_handlers(app)

    me = SimpleNamespace(id=uuid4(), role=UserRole.ADMIN)
    app.dependency_overrides[get_category_service] = lambda: service_mock
    app.dependency_overrides[Authenticated.dependency] = lambda: me
    app.dependency_overrides[Admin.dependency] = lambda: me

    return TestClient(app), me


def test_create_calls_service_and_returns_category():
    """
    Test that the create category endpoint calls the service and returns the created category.

    - Asserts that the service's create method is called with the correct model.
    - Checks that the API returns the expected HTTP response and body.
    """
    service = Mock()
    category_id = uuid4()
    payload = {"name": "python", "description": "Python topics"}

    client, _ = _build_client(service)
    service.create.return_value = _category_read_obj(
        category_id, name=payload["name"], description=payload["description"]
    )

    response = client.post("/categories", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == str(category_id)
    assert body["data"]["name"] == payload["name"]
    assert body["data"]["description"] == payload["description"]

    assert service.create.call_count == 1
    (create_model,) = service.create.call_args.args
    assert create_model.model_dump() == payload


def test_list_returns_categories():
    """
    Test that the list categories endpoint returns the expected categories.

    - Mocks the service to return one category, and checks the HTTP response body shape.
    """
    service = Mock()
    cid = uuid4()
    service.list.return_value = [_category_read_obj(cid, name="a", description="d")]

    client, _ = _build_client(service)
    response = client.get("/categories")

    assert response.status_code == 200
    body = response.json()
    assert len(body["data"]) == 1
    assert body["data"][0]["id"] == str(cid)
    assert body["data"][0]["name"] == "a"
    service.list.assert_called_once_with()


def test_get_by_id_returns_category():
    """
    Test that getting a category by ID returns the expected category.

    - Ensures service is called with a string UUID.
    - Validates HTTP status and response body.
    """
    service = Mock()
    category_id = uuid4()
    service.get_by_id.return_value = _category_read_obj(category_id)

    client, _ = _build_client(service)
    response = client.get(f"/categories/{category_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == str(category_id)
    service.get_by_id.assert_called_once_with(str(category_id))


def test_get_by_id_returns_404_when_not_found():
    """
    Test that getting a category by an unknown ID returns a 404 response.

    - Mocks the service to raise NotFoundException.
    - Asserts the HTTP error response shape.
    """
    service = Mock()
    category_id = uuid4()
    service.get_by_id.side_effect = NotFoundError(message="Category not found")

    client, _ = _build_client(service)
    response = client.get(f"/categories/{category_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Category not found"}
    }


def test_partial_update_calls_service_and_returns_category():
    """
    Test that partially updating a category calls the service and returns the updated category.

    - Checks that the service's partial_update is called with appropriate arguments and
      the response reflects the update.
    """
    service = Mock()
    category_id = uuid4()
    payload = {"name": "new", "description": "new desc"}

    client, _ = _build_client(service)
    service.partial_update.return_value = _category_read_obj(
        category_id, name=payload["name"], description=payload["description"]
    )

    response = client.patch(f"/categories/{category_id}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["name"] == payload["name"]

    assert service.partial_update.call_count == 1
    called_id, update_model = service.partial_update.call_args.args
    assert called_id == str(category_id)
    assert update_model.model_dump() == payload


def test_delete_returns_204_and_calls_service():
    """
    Test that deleting a category calls the service and returns a 204 no content response.

    - Asserts that service.delete_category is called with the proper category id.
    - Checks the response is HTTP 204 and has empty content.
    """
    service = Mock()
    category_id = uuid4()

    client, _ = _build_client(service)
    response = client.delete(f"/categories/{category_id}")

    assert response.status_code == 204
    assert response.content == b""
    service.delete_category.assert_called_once_with(str(category_id))

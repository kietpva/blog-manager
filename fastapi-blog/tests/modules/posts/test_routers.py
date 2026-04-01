from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import Mock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.exceptions import NotFoundException, register_exception_handlers
from app.dependencies.posts import get_post_service
from app.dependencies.rbac import Authenticated
from app.modules.posts.routers import router
from app.modules.users.models import UserRole
from app.utils.pagination import PaginationInfo


def _post_read_obj(post_id, author_id, title="Title", content="Content"):
    """
    Create a SimpleNamespace representing the API response for a post.

    Args:
        post_id: The UUID of the post.
        author_id: The UUID of the post's author.
        title (str, optional): The title of the post. Defaults to "Title".
        content (str, optional): The content/body of the post. Defaults to "Content".

    Returns:
        SimpleNamespace: An object simulating the post API response.
    """
    return SimpleNamespace(
        id=post_id,
        title=title,
        content=content,
        author_id=author_id,
        created_at=datetime.now(timezone.utc),
        categories=[],
    )


def _build_client(service_mock: Mock) -> tuple[TestClient, SimpleNamespace]:
    """
    Build a FastAPI TestClient with necessary dependency overrides for testing.

    Args:
        service_mock (Mock): A unittest.mock.Mock for the post service.

    Returns:
        tuple[TestClient, SimpleNamespace]: The test client and mock user.
    """
    app = FastAPI()
    app.include_router(router)
    register_exception_handlers(app)

    me = SimpleNamespace(id=uuid4(), role=UserRole.admin)
    app.dependency_overrides[get_post_service] = lambda: service_mock
    # Override the underlying function used by Authenticated and get_current_active_user.
    app.dependency_overrides[Authenticated.dependency] = lambda: me

    return TestClient(app), me


def test_get_by_id_returns_post():
    """
    Test that a GET by post ID returns the correct post data.
    """
    service = Mock()
    post_id = uuid4()
    author_id = uuid4()
    service.get_by_id.return_value = _post_read_obj(post_id, author_id)

    client, _ = _build_client(service)
    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == str(post_id)
    assert body["data"]["author_id"] == str(author_id)
    service.get_by_id.assert_called_once_with(post_id)


def test_get_by_id_returns_404_when_service_raises_not_found():
    """
    Test that GET by ID returns 404 if the service raises NotFoundException.
    """
    service = Mock()
    post_id = uuid4()
    service.get_by_id.side_effect = NotFoundException(message="Post not found")

    client, _ = _build_client(service)
    response = client.get(f"/posts/{post_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "not_found", "message": "Post not found"}
    }


def test_list_returns_paginated_posts():
    """
    Test that listing posts returns paginated data with expected metadata.
    """
    service = Mock()
    post_id = uuid4()
    author_id = uuid4()

    page = PaginationInfo(total=1, limit=10, offset=0, hasNext=False, hasPrev=False)
    service.list.return_value = (page, [_post_read_obj(post_id, author_id)])

    client, _ = _build_client(service)
    response = client.get("/posts?limit=10&offset=0")

    assert response.status_code == 200
    body = response.json()
    assert body["data"][0]["id"] == str(post_id)
    assert body["meta"]["pagination"]["total"] == 1
    assert body["meta"]["pagination"]["hasNext"] is False
    service.list.assert_called_once_with(10, 0)


def test_create_calls_service_and_returns_post():
    """
    Test that creating a post calls the service and returns the created post.
    """
    service = Mock()
    post_id = uuid4()
    payload = {"title": "New title", "content": "Body", "category_ids": []}

    client, me = _build_client(service)
    service.create.return_value = _post_read_obj(post_id, author_id=me.id, title=payload["title"])

    response = client.post("/posts", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["id"] == str(post_id)
    assert body["data"]["author_id"] == str(me.id)

    assert service.create.call_count == 1
    post_create_model, passed_author_id = service.create.call_args.args
    assert passed_author_id == me.id
    assert post_create_model.model_dump() == payload


def test_partial_update_calls_service_and_returns_post():
    """
    Test that partially updating a post calls the service and returns the updated result.
    """
    service = Mock()
    post_id = uuid4()
    author_id = uuid4()

    client, me = _build_client(service)
    service.partial_update.return_value = _post_read_obj(
        post_id, author_id=author_id, title="Updated title"
    )

    response = client.patch(f"/posts/{post_id}", json={"title": "Updated title"})

    assert response.status_code == 200
    body = response.json()
    assert body["data"]["title"] == "Updated title"

    assert service.partial_update.call_count == 1
    called_post_id, post_update_model, called_current_user = service.partial_update.call_args.args
    assert called_post_id == post_id
    assert called_current_user is me
    assert post_update_model.model_dump(exclude_unset=True) == {"title": "Updated title"}


def test_delete_returns_204_and_calls_service():
    """
    Test that deleting a post returns 204 and calls the service's delete method.
    """
    service = Mock()
    post_id = uuid4()

    client, me = _build_client(service)
    response = client.delete(f"/posts/{post_id}")

    assert response.status_code == 204
    assert service.delete.call_count == 1
    called_post_id, called_current_user = service.delete.call_args.args
    assert called_post_id == post_id
    assert called_current_user is me


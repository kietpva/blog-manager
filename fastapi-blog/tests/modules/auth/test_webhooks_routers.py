from __future__ import annotations

from unittest.mock import Mock

from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from app.core.exceptions import register_exception_handlers
from app.dependencies.users import get_user_service
from app.modules.webhooks import routers


def _build_client(service_mock: Mock) -> TestClient:
    """
    Helper function to build a FastAPI TestClient with the auth router registered,
    exception handlers set up, and the user service dependency overridden with the provided mock.

    Args:
        service_mock (Mock): Mock object to use in place of the actual user service.

    Returns:
        TestClient: Configured FastAPI test client instance.
    """
    app = FastAPI()
    app.include_router(routers.router)
    register_exception_handlers(app)
    app.dependency_overrides[get_user_service] = lambda: service_mock
    return TestClient(app)


def test_clerk_webhook_returns_400_on_verification_error(monkeypatch):
    """
    Test that when the webhook signature verification fails,
    the endpoint returns HTTP 400 Bad Request
    and does not attempt to create a user.
    """
    from svix.webhooks import WebhookVerificationError

    service = Mock()
    client = _build_client(service)

    class FakeWebhook:
        def __init__(self, _secret):
            pass

        def verify(self, _payload, _headers):
            raise WebhookVerificationError("invalid")

    monkeypatch.setattr(routers, "Webhook", FakeWebhook)

    response = client.post("/webhooks/clerk", data=b"{}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    service.create.assert_not_called()


def test_clerk_webhook_returns_204_when_auth_id_missing(monkeypatch):
    """
    Test that if a 'user_created' event does not include an 'id' (auth_id), the endpoint returns
    HTTP 204 No Content and does not create a user.
    """
    service = Mock()
    client = _build_client(service)

    class FakeWebhook:
        def __init__(self, _secret):
            pass

        def verify(self, _payload, _headers):
            return {"type": routers.ClerkEventEnum.USER_CREATED, "data": {}}

    monkeypatch.setattr(routers, "Webhook", FakeWebhook)

    response = client.post("/webhooks/clerk", json={})

    assert response.status_code == status.HTTP_204_NO_CONTENT
    service.create.assert_not_called()


def test_clerk_webhook_creates_user_on_user_created_event(monkeypatch):
    """
    Test that when a valid 'user_created' event payload is posted, the webhook parses out the fields
    (auth_id, email, first_name, last_name) and invokes the user creation service with those values.
    The endpoint should return HTTP 204 No Content.
    """
    service = Mock()
    client = _build_client(service)

    class FakeWebhook:
        def __init__(self, _secret):
            pass

        def verify(self, _payload, _headers):
            return {
                "type": routers.ClerkEventEnum.USER_CREATED,
                "data": {
                    "id": "auth_123",
                    "email_addresses": [{"email_address": "user@example.com"}],
                    "first_name": "John",
                    "last_name": "Doe",
                },
            }

    monkeypatch.setattr(routers, "Webhook", FakeWebhook)

    response = client.post("/webhooks/clerk", data=b"ignored")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    service.create.assert_called_once()
    args, _ = service.create.call_args
    user_create = args[0]
    assert user_create.auth_id == "auth_123"
    assert user_create.email == "user@example.com"
    assert user_create.first_name == "John"
    assert user_create.last_name == "Doe"

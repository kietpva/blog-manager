from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.exceptions import AppError, ErrorCode, NotFoundError, StatusCode


def test_get_current_user_raises_unauthorized_when_clerk_id_missing():
    """
    Test that get_current_user raises AppError(unauthorized)
    if no clerk_id is set on the request object state.
    """
    from app.dependencies.auth import get_current_user

    request = SimpleNamespace(state=SimpleNamespace())

    with pytest.raises(AppError) as exc_info:
        get_current_user(request)

    assert exc_info.value.code == ErrorCode.UNAUTHORIZED
    assert exc_info.value.message == "Not authenticated"
    assert exc_info.value.status_code == StatusCode.UNAUTHORIZED


def test_get_current_user_raises_not_found_when_db_returns_none(
    monkeypatch: pytest.MonkeyPatch,
):
    """
    Test that get_current_user raises NotFoundError (404, not_found)
    when no user is found in the database for the provided clerk_id.
    """
    from app.dependencies import auth

    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = None
    monkeypatch.setattr(auth, "SessionLocal", lambda: db)

    request = SimpleNamespace(state=SimpleNamespace(clerk_id="clerk_123"))

    with pytest.raises(NotFoundError) as exc_info:
        auth.get_current_user(request)

    assert exc_info.value.code == ErrorCode.NOT_FOUND
    assert exc_info.value.message == "User does not exist"
    assert exc_info.value.status_code == StatusCode.NOT_FOUND
    db.close.assert_called_once_with()


def test_get_current_user_returns_user_when_found(monkeypatch: pytest.MonkeyPatch):
    """
    Test that get_current_user returns the user instance
    when a user with the given clerk_id exists in the database.
    """
    from app.dependencies import auth
    from app.modules.users.models import User

    fake_user = User(
        auth_id="clerk_123",
        email="user@example.com",
        first_name="John",
        last_name="Doe",
    )

    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = fake_user
    monkeypatch.setattr(auth, "SessionLocal", lambda: db)

    request = SimpleNamespace(state=SimpleNamespace(clerk_id="clerk_123"))

    result = auth.get_current_user(request)

    assert result is fake_user
    db.query.assert_called_once_with(User)
    db.close.assert_called_once_with()


def test_get_current_active_user_raises_forbidden_when_user_inactive():
    """
    Test that get_current_active_user raises AppError(forbidden)
    if the provided user object is inactive.
    """
    from app.dependencies.auth import get_current_active_user

    inactive_user = SimpleNamespace(is_active=False)

    with pytest.raises(AppError) as exc_info:
        get_current_active_user(inactive_user)

    assert exc_info.value.code == ErrorCode.FORBIDDEN
    assert exc_info.value.message == "Inactive user"
    assert exc_info.value.status_code == StatusCode.FORBIDDEN


def test_get_current_active_user_returns_user_when_active():
    """
    Test that get_current_active_user returns the user object when
    the user is active.
    """
    from app.dependencies.auth import get_current_active_user

    active_user = SimpleNamespace(is_active=True)

    result = get_current_active_user(active_user)

    assert result is active_user

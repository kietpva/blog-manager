from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.decorators.permissions import check_permission
from app.modules.users.models import UserRole


def test_check_permission_allows_admin_for_any_owner():
    """
    Test that check_permission allows an admin user to access any resource,
    regardless of the owner_id. Should not raise and should return True.
    """
    current_user = SimpleNamespace(id="u1", role=UserRole.ADMIN)
    assert check_permission(current_user, owner_id="someone") is True


def test_check_permission_allows_owner_for_self():
    """
    Test that check_permission allows a user to access their own resource,
    i.e., when current_user.id matches owner_id. Should return True.
    """
    current_user = SimpleNamespace(id="owner-id", role=UserRole.USER)
    assert check_permission(current_user, owner_id="owner-id") is True


def test_check_permission_denies_non_owner_user():
    """
    Test that check_permission denies access for a non-admin user when their id
    does not match the resource's owner_id. Should raise AppError with forbidden code.
    """
    current_user = SimpleNamespace(id="u1", role=UserRole.USER)

    with pytest.raises(AppError) as exc_info:
        check_permission(current_user, owner_id="owner-id")

    err = exc_info.value
    assert err.code == ErrorCode.FORBIDDEN
    assert err.message == "Permission denied"
    assert err.status_code == StatusCode.FORBIDDEN

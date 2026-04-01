from __future__ import annotations

from types import SimpleNamespace

import pytest

from app.core.exceptions import AppError, ErrorCode, StatusCode
from app.decorators.roles import require_roles
from app.modules.users.models import UserRole


def test_require_roles_allows_when_role_enum_matches():
    """
    Ensure require_roles allows access when user's role matches
    required role, given as UserRole enum.
    """
    dependency = require_roles(UserRole.admin)
    current_user = SimpleNamespace(id="u1", role=UserRole.admin)

    assert dependency(current_user) is current_user


def test_require_roles_allows_when_role_str_matches():
    """
    Ensure require_roles allows access when user's role matches
    required role, given as string equivalent of UserRole enum.
    """
    dependency = require_roles(UserRole.admin)
    current_user = SimpleNamespace(id="u1", role="admin")

    assert dependency(current_user) is current_user


def test_require_roles_denies_when_role_not_allowed():
    """
    Ensure require_roles raises AppError with forbidden status when
    user's role does not match required role.
    """
    dependency = require_roles(UserRole.admin)
    current_user = SimpleNamespace(id="u1", role=UserRole.user)

    with pytest.raises(AppError) as exc_info:
        dependency(current_user)

    err = exc_info.value
    assert err.code == ErrorCode.forbidden
    assert err.message == "Permission denied"
    assert err.status_code == StatusCode.forbidden

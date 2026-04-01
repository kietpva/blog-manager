from __future__ import annotations

import importlib
from unittest.mock import Mock

import pytest

from app.core.exceptions import AppError, ErrorCode, StatusCode


@pytest.fixture(autouse=True)
def _set_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Automatically set required environment variables for Clerk and database config
    before each test, to ensure that `app.core.config.Settings()` and `app.core.jwt`
    can be imported without errors.
    """
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    monkeypatch.setenv("CLERK_ISSUER", "test-issuer")
    monkeypatch.setenv(
        "CLERK_JWKS_URL", "https://example.invalid/.well-known/jwks.json"
    )
    monkeypatch.setenv("CLERK_WEBHOOK_SECRET", "test-secret")
    monkeypatch.setenv("DEBUG", "False")


def _reload_jwt_module():
    """
    Helper to reload the `app.core.jwt` module so that its module-scoped
    state (like `_jwks_cache`) is reset for each test.
    Returns the reloaded module object.
    """
    jwt_module = importlib.import_module("app.core.jwt")
    return importlib.reload(jwt_module)


def test_get_jwks_returns_cached_value_without_http_call():
    """
    Assert that calling `get_jwks` returns the cached JWKS value if set,
    and does not invoke any HTTP calls to the JWKS endpoint.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = {"cached": True}

    jwt_module.httpx.get = Mock(side_effect=AssertionError("should not call httpx.get"))

    assert jwt_module.get_jwks() == {"cached": True}


def test_get_jwks_fetches_and_caches_result():
    """
    Assert that `get_jwks` fetches and caches the JWKS when the cache is empty,
    and that the returned object is as expected.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = None

    res = Mock()
    res.json.return_value = {"keys": [{"kid": "kid1"}]}
    jwt_module.httpx.get = Mock(return_value=res)

    out = jwt_module.get_jwks()

    assert out == {"keys": [{"kid": "kid1"}]}
    res.raise_for_status.assert_called_once_with()
    jwt_module.httpx.get.assert_called_once()
    assert jwt_module._jwks_cache == {"keys": [{"kid": "kid1"}]}


def test_get_jwks_raises_service_unavailable_on_fetch_exception():
    """
    Assert that `get_jwks` raises AppError with service_unavailable code
    if there is an exception while fetching JWKS.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = None

    jwt_module.httpx.get = Mock(side_effect=Exception("network down"))

    with pytest.raises(AppError) as exc_info:
        jwt_module.get_jwks()

    assert exc_info.value.code == ErrorCode.service_unavailable
    assert exc_info.value.message == "Unable to fetch JWKS"
    assert exc_info.value.status_code == StatusCode.service_unavailable


def test_get_public_key_raises_unauthorized_when_header_is_invalid():
    """
    Assert that `get_public_key` raises AppError with unauthorized code
    if the JWT header is invalid and cannot be parsed.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = None

    jwt_module.jwt.get_unverified_header = Mock(
        side_effect=jwt_module.JWTError("invalid header")
    )

    with pytest.raises(AppError) as exc_info:
        jwt_module.get_public_key("any-token")

    assert exc_info.value.code == ErrorCode.unauthorized
    assert exc_info.value.message == "Invalid token header"
    assert exc_info.value.status_code == StatusCode.unauthorized


def test_get_public_key_raises_unauthorized_when_kid_missing():
    """
    Assert that `get_public_key` raises AppError with unauthorized code
    if the JWT header does not contain a `kid` field.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = None

    jwt_module.jwt.get_unverified_header = Mock(return_value={})

    with pytest.raises(AppError) as exc_info:
        jwt_module.get_public_key("any-token")

    assert exc_info.value.code == ErrorCode.unauthorized
    assert exc_info.value.message == "Token missing kid"
    assert exc_info.value.status_code == StatusCode.unauthorized


def test_get_public_key_returns_matching_key():
    """
    Assert that `get_public_key` returns the correct public key when the JWT `kid`
    matches a JWKS key.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = None

    jwt_module.jwt.get_unverified_header = Mock(return_value={"kid": "kid1"})
    jwt_module.get_jwks = Mock(
        return_value={
            "keys": [
                {"kid": "kid1", "kty": "RSA", "use": "sig"},
                {"kid": "kid2", "kty": "RSA", "use": "sig"},
            ]
        }
    )

    assert jwt_module.get_public_key("any-token")["kid"] == "kid1"


def test_get_public_key_raises_unauthorized_when_key_not_found():
    """
    Assert that `get_public_key` raises AppError with unauthorized code
    if no matching public key is found for the given JWT `kid`.
    """
    jwt_module = _reload_jwt_module()
    jwt_module._jwks_cache = None

    jwt_module.jwt.get_unverified_header = Mock(return_value={"kid": "kidX"})
    jwt_module.get_jwks = Mock(return_value={"keys": [{"kid": "kid1"}]})

    with pytest.raises(AppError) as exc_info:
        jwt_module.get_public_key("any-token")

    assert exc_info.value.code == ErrorCode.unauthorized
    assert exc_info.value.message == "Public key not found"
    assert exc_info.value.status_code == StatusCode.unauthorized


def test_verify_auth_token_returns_payload_on_success():
    """
    Assert that `verify_auth_token` returns the expected JWT payload
    when token verification and decoding succeed.
    """
    jwt_module = _reload_jwt_module()

    jwt_module.get_public_key = Mock(return_value={"kid": "kid1"})
    jwt_module.jwt.decode = Mock(return_value={"sub": "user_123"})

    assert jwt_module.verify_auth_token("token") == {"sub": "user_123"}
    jwt_module.jwt.decode.assert_called_once()


def test_verify_auth_token_raises_unauthorized_on_decode_jwterror():
    """
    Assert that `verify_auth_token` raises AppError with unauthorized code
    if decoding the JWT fails (e.g., signature or expiry issue).
    """
    jwt_module = _reload_jwt_module()

    jwt_module.get_public_key = Mock(return_value={"kid": "kid1"})
    jwt_module.jwt.decode = Mock(side_effect=jwt_module.JWTError("expired"))

    with pytest.raises(AppError) as exc_info:
        jwt_module.verify_auth_token("token")

    assert exc_info.value.code == ErrorCode.unauthorized
    assert exc_info.value.message == "Invalid or expired token"
    assert exc_info.value.status_code == StatusCode.unauthorized

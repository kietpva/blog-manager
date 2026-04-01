from __future__ import annotations


def test_extract_email_returns_none_when_no_email_addresses():
    from app.utils.helpers import extract_email

    data = {}
    assert extract_email(data) is None


def test_extract_email_returns_first_email_address():
    from app.utils.helpers import extract_email

    data = {
        "email_addresses": [
            {"email_address": "a@example.com"},
            {"email_address": "b@example.com"},
        ]
    }
    assert extract_email(data) == "a@example.com"


def test_extract_first_name_returns_empty_string_when_missing():
    from app.utils.helpers import extract_first_name

    assert extract_first_name({}) == ""


def test_extract_last_name_returns_empty_string_when_missing():
    from app.utils.helpers import extract_last_name

    assert extract_last_name({}) == ""


def test_apply_partial_update_only_updates_existing_attributes():
    from app.utils.helpers import apply_partial_update

    class FakeUser:
        def __init__(self):
            self.first_name = "Old"

    instance = FakeUser()

    updated = apply_partial_update(
        instance=instance,
        data={"first_name": "New", "unknown_field": "SHOULD_NOT_SET"},
    )

    assert updated is instance
    assert instance.first_name == "New"
    assert not hasattr(instance, "unknown_field")

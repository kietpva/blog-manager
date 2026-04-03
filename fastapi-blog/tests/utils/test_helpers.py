from __future__ import annotations


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

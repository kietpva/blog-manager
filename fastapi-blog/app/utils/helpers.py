def extract_email(data: dict) -> str | None:
    """
    Extracts the primary email address from the given data dictionary.
    """
    emails = data.get("email_addresses", [])
    if not emails:
        return None
    return emails[0].get("email_address")


def extract_first_name(data: dict) -> str:
    """
    Extracts the user's first name from the given data dictionary.
    """
    return data.get("first_name") or ""


def extract_last_name(data: dict) -> str:
    """
    Extracts the user's last name from the given data dictionary.
    """
    return data.get("last_name") or ""


def apply_partial_update(*, instance, data):
    """
    Apply partial updates to an instance using values from a Pydantic model.

    Args:
        instance: The object to apply the updates to.
        data: A Pydantic model containing the fields to update.

    Returns:
        The updated instance.
    """
    for key, value in data.items():
        if hasattr(instance, key):
            setattr(instance, key, value)
    return instance

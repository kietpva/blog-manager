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

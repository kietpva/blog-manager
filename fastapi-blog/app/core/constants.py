from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel


T = TypeVar("T")


class ResponseData(BaseModel, Generic[T]):
    """
    Represents the response schema for user data.

    Used in API responses to return user information.
    """

    data: T

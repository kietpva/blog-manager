from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

from app.utils.pagination import Meta


T = TypeVar("T")


class ResponseData(BaseModel, Generic[T]):
    """
    Generic API response wrapper.

    Attributes:
        data (T): The main response data, generic type.
    """

    data: T


class PaginationResponse(ResponseData):
    """
    API response model for paginated results.

    Inherits from ResponseData and adds a meta field containing pagination metadata.

    Attributes:
        data (T): The main response data, generic type (usually a list of items).
        meta (Meta): Metadata with pagination information.
    """

    meta: Meta

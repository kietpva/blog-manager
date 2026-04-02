from pydantic import BaseModel

MAX_ITEMS_PER_PAGE: int = 100


class PaginationInfo(BaseModel):
    """
    Pagination metadata structure.

    Attributes:
        total (int): The total number of items available.
        limit (int): The maximum number of items returned per page.
        offset (int): The number of items skipped before collecting the result set.
        has_mext (bool): Whether there is a next page of items.
        has_prev (bool): Whether there is a previous page of items.
    """

    total: int
    limit: int
    offset: int
    has_next: bool
    has_prev: bool


class Meta(BaseModel):
    """
    Metadata wrapper model.

    Attributes:
        pagination (PaginationInfo): Pagination information for the current response.
    """

    pagination: PaginationInfo


def build_pagination(total: int, limit: int, offset: int) -> PaginationInfo:
    """
    Construct a PaginationInfo instance based on total items, limit, and offset.

    Args:
        total (int): The total number of items available across all pages.
        limit (int): The maximum number of items per page.
        offset (int): The number of items skipped (start index for the current page).

    Returns:
        PaginationInfo: Metadata object containing pagination details for the current query.
    """
    return PaginationInfo(
        total=total,
        limit=limit,
        offset=offset,
        has_next=offset + limit < total,
        has_prev=offset > 0,
    )

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.core.constants import MAX_ITEMS_PER_PAGE
from app.core.exceptions import StatusCode
from app.dependencies.auth import get_current_active_user
from app.dependencies.posts import get_post_service
from app.dependencies.rbac import Authenticated
from app.modules.posts.schemas import PostCreate, PostResponse, PostUpdate
from app.modules.posts.services import PostService
from app.utils.pagination import (
    Meta,
    PaginationResponse,
    ResponseData,
)

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post(
    "",
    response_model=ResponseData[PostResponse],
    dependencies=[Authenticated],
)
def create(
    payload: PostCreate,
    current_user=Depends(get_current_active_user),
    service: PostService = Depends(get_post_service),
):
    """
    Create a new post.

    Args:
        payload (PostCreate): The post data to create.
        current_user: The currently authenticated user (injected via dependency).
        service (PostService): The post service instance (injected via dependency).

    Returns:
        ResponseData[PostResponse]: The created post wrapped in a response model.
    """
    data = service.create(payload, current_user.id)
    return ResponseData[PostResponse](data=data)


@router.get(
    "/{post_id}",
    response_model=ResponseData[PostResponse],
    dependencies=[Authenticated],
)
def get_by_id(
    post_id: UUID,
    service: PostService = Depends(get_post_service),
):
    """
    Retrieve a single post by its unique identifier.

    Args:
        post_id (UUID): The unique identifier of the post to retrieve.
        service (PostService): The post service instance (injected via dependency).

    Returns:
        ResponseData[PostResponse]: The specified post wrapped in a response model.
    """
    data = service.get_by_id(post_id)
    return ResponseData[PostResponse](data=data)


@router.get(
    "",
    response_model=PaginationResponse[list[PostResponse]],
    dependencies=[Authenticated],
)
def posts(
    limit: int = Query(10, ge=1, le=MAX_ITEMS_PER_PAGE),
    offset: int = Query(0, ge=0),
    service: PostService = Depends(get_post_service),
):
    """
    Retrieve a list of all posts.

    Args:
        limit (int): Maximum number of posts to return (default: 10).
        offset (int): Number of posts to skip (default: 0).
        service (PostService): Injected PostService instance.

    Returns:
        PaginationResponse[list[PostResponse]]: Paginated post list and pagination info.
    """

    pagination, items = service.list(limit, offset)

    return PaginationResponse[list[PostResponse]](
        data=items,
        meta=Meta(pagination=pagination),
    )


@router.patch(
    "/{post_id}",
    response_model=ResponseData[PostResponse],
    dependencies=[Authenticated],
)
def partial_update(
    post_id: UUID,
    payload: PostUpdate,
    current_user=Depends(get_current_active_user),
    service: PostService = Depends(get_post_service),
):
    """
    Update an existing post's details.

    Args:
        post_id (UUID): The unique identifier of the post to update.
        payload (PostUpdate): The update data for the post.
        current_user: The currently authenticated user (injected via dependency).
        service (PostService): The post service instance (injected via dependency).

    Returns:
        ResponseData[PostResponse]: The updated post wrapped in a response model.
    """
    data = service.partial_update(post_id, payload, current_user)
    return ResponseData[PostResponse](data=data)


@router.delete(
    "/{post_id}",
    dependencies=[Authenticated],
    status_code=StatusCode.NO_CONTENT,
)
def delete(
    post_id: UUID,
    current_user=Depends(get_current_active_user),
    service: PostService = Depends(get_post_service),
):
    """
    Delete an existing post.

    Args:
        post_id (UUID): The unique identifier of the post to delete.
        current_user: The currently authenticated user (injected via dependency).
        service (PostService): The post service instance (injected via dependency).

    Returns:
        None
    """
    service.delete(post_id, current_user)
    return

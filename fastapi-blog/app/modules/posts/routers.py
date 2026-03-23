from fastapi import APIRouter, Depends
from uuid import UUID

from app.core.constants import ResponseData
from app.core.exceptions import StatusCode
from app.dependencies.posts import get_post_service
from app.dependencies.rbac import Authenticated
from app.modules.posts.services import PostService
from app.modules.posts.schemas import PostCreate, PostUpdate, PostResponse
from app.dependencies.auth import get_current_active_user

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post(
    "",
    response_model=ResponseData[PostResponse],
    dependencies=[Authenticated],
)
def create_post(
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
    post = service.create_post(payload, current_user.id)
    return ResponseData[PostResponse](data=post)


@router.get(
    "/{post_id}",
    response_model=ResponseData[PostResponse],
    dependencies=[Authenticated],
)
def get_post(
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
    post = service.get_post(post_id)
    return ResponseData[PostResponse](data=post)


@router.get(
    "",
    response_model=ResponseData[list[PostResponse]],
    dependencies=[Authenticated],
)
def get_posts(service: PostService = Depends(get_post_service)):
    """
    Retrieve a list of all posts.

    Args:
        service (PostService): The post service instance (injected via dependency).

    Returns:
        ResponseData[list[PostResponse]]: A list of all posts wrapped in a response model.
    """
    posts = service.get_posts()
    return ResponseData[list[PostResponse]](data=posts)


@router.patch(
    "/{post_id}",
    response_model=ResponseData[PostResponse],
    dependencies=[Authenticated],
)
def update_post(
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
    post = service.update_post(post_id, payload, current_user)
    return ResponseData[PostResponse](data=post)


@router.delete(
    "/{post_id}",
    dependencies=[Authenticated],
    status_code=StatusCode.no_content,
)
def delete_post(
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
    service.delete_post(post_id, current_user)
    return


@router.get("/test-error")
def test_error():
    raise Exception("Something went wrong")

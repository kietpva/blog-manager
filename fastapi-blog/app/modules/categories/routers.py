from typing import List
from fastapi import APIRouter, Depends
from app.core.exceptions import StatusCode
from app.dependencies.categories import get_category_service
from app.dependencies.rbac import Admin, Authenticated
from app.modules.categories.services import CategoryService
from app.modules.categories.schemas import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
)
from app.core.constants import ResponseData

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=ResponseData[CategoryResponse],
    dependencies=[Admin],
)
def create(
    data: CategoryCreate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Create a new category.

    Args:
        data (CategoryCreate): The category data to create.
        service (CategoryService): Injected dependency providing category operations.

    Returns:
        ResponseData[CategoryResponse]: The created category wrapped in a response model.
    """
    data = service.create(data)
    return ResponseData[CategoryResponse](data=data)


@router.get(
    "",
    response_model=ResponseData[List[CategoryResponse]],
    dependencies=[Authenticated],
)
def list(
    service: CategoryService = Depends(get_category_service),
):
    """
    Retrieve all categories.

    Args:
        service (CategoryService): Injected dependency providing category operations.

    Returns:
        ResponseData[list[CategoryResponse]]: A list of all categories in a response model.
    """
    data = service.list()
    return ResponseData[List[CategoryResponse]](data=data)


@router.get(
    "/{category_id}",
    response_model=ResponseData[CategoryResponse],
    dependencies=[Authenticated],
)
def get_by_id(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
):
    """
    Retrieve a single category by its ID.

    Args:
        category_id (str): The unique identifier of the category.
        service (CategoryService): Injected dependency providing category operations.

    Returns:
        ResponseData[CategoryResponse]: The specified category in a response model.
    """
    data = service.get_by_id(category_id)
    return ResponseData[CategoryResponse](data=data)


@router.patch(
    "/{category_id}",
    response_model=ResponseData[CategoryResponse],
    dependencies=[Admin],
)
def partial_update(
    category_id: str,
    data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service),
):
    """
    Update the details of an existing category.

    Args:
        category_id (str): The unique identifier of the category to update.
        data (CategoryUpdate): The updated category information.
        service (CategoryService): Injected dependency providing category operations.

    Returns:
        ResponseData[CategoryResponse]: The updated category in a response model.
    """
    result = service.partial_update(category_id, data)
    return ResponseData[CategoryResponse](data=result)


@router.delete(
    "/{category_id}",
    dependencies=[Admin],
    status_code=StatusCode.no_content,
)
def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service),
):
    """
    Delete a category.

    Args:
        category_id (str): The unique identifier of the category to delete.
        service (CategoryService): Injected dependency providing category operations.

    Returns:
        None
    """
    service.delete_category(category_id)
    return

from unittest.mock import Mock, patch

from app.core.constants import SortOrder
from app.modules.users.models import User
from app.modules.users.repositories import UserRepository
from app.utils.pagination import PaginationInfo


def test_get_by_auth_id_builds_expected_query_chain():
    """
    Test that UserRepository.get_by_auth_id constructs and executes
    the expected database query chain to retrieve a user by auth_id.

    The test verifies that:
      - The query builder is chained correctly: query -> filter -> one_or_none
      - The expected User is returned from the method
      - Each method in the query chain is called exactly once with expected arguments
    """
    db = Mock()
    query = Mock()
    filtered = Mock()
    expected_user = Mock(spec=User)

    db.query.return_value = query
    query.filter.return_value = filtered
    filtered.one_or_none.return_value = expected_user

    repo = UserRepository(db)
    result = repo.get_by_auth_id("auth_123")

    assert result is expected_user
    db.query.assert_called_once_with(User)
    query.filter.assert_called_once()
    filtered.one_or_none.assert_called_once_with()


def test_list_delegates_to_base_repository_with_created_at_desc_order():
    """
    Test that UserRepository.list delegates to BaseRepository.list
    with proper ordering by 'created_at' in descending order.

    The test verifies that:
      - UserRepository.list calls the base repository's list method
      with the expected limit and offset
      - The 'order_by' keyword argument is included and applies to the 'created_at' field
      - The returned pagination and items match the expected values
      - The base list method is called exactly once
    """
    db = Mock()
    repo = UserRepository(db)
    expected_page = PaginationInfo(
        total=1,
        limit=10,
        offset=0,
        has_next=False,
        has_prev=False,
    )
    expected_items = [Mock(spec=User)]

    with patch("app.modules.users.repositories.BaseRepository.list") as base_list_mock:
        base_list_mock.return_value = (expected_page, expected_items)

        result_page, result_items = repo.list(limit=10, offset=0)

    assert result_page is expected_page
    assert result_items == expected_items
    base_list_mock.assert_called_once()

    args, kwargs = base_list_mock.call_args
    assert args == (10, 0)
    assert "order_by" in kwargs
    assert kwargs["order_by"] == SortOrder.NEWEST

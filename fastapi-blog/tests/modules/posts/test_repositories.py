from unittest.mock import Mock, patch
from uuid import uuid4

from app.modules.categories.models import Category
from app.modules.posts.models import Post
from app.modules.posts.repositories import PostRepository


def test_list_delegates_to_base_repository_with_order_and_selectinload():
    """
    Test that PostRepository.list delegates to BaseRepository.list with the correct arguments,
    specifically ensuring it passes the expected 'order_by' (on 'created_at') and 'options'
    (using selectinload for Post.categories).

    - Verifies exact options object passed to BaseRepository.list.
    - Asserts return values are as expected from the mocked base list method.
    """
    db = Mock()
    repo = PostRepository(db)

    expected_page = Mock()
    expected_items = [Mock(spec=Post)]

    # Patch `selectinload` to a sentinel so we can assert the exact `options` object
    # passed into BaseRepository.list (SQLAlchemy's Load() string repr is not stable).
    selectinload_sentinel = object()
    with (
        patch("app.modules.posts.repositories.selectinload") as selectinload_mock,
        patch("app.modules.posts.repositories.BaseRepository.list") as base_list_mock,
    ):
        selectinload_mock.return_value = selectinload_sentinel
        base_list_mock.return_value = (expected_page, expected_items)

        result_page, result_items = repo.list(limit=10, offset=0)

    assert result_page is expected_page
    assert result_items == expected_items

    base_list_mock.assert_called_once()
    args, kwargs = base_list_mock.call_args
    assert args == (10, 0)
    assert "order_by" in kwargs
    assert "created_at" in str(kwargs["order_by"])

    assert "options" in kwargs
    assert kwargs["options"] is not None
    assert len(kwargs["options"]) == 1
    assert kwargs["options"][0] is selectinload_sentinel
    selectinload_mock.assert_called_once_with(Post.categories)


def test_get_categories_by_ids_returns_empty_when_no_ids():
    """
    Test that PostRepository.get_categories_by_ids returns an empty list and does not query
    the database when an empty list of IDs is provided.
    """
    db = Mock()
    repo = PostRepository(db)
    result = repo.get_categories_by_ids([])

    assert result == []
    db.query.assert_not_called()


def test_get_categories_by_ids_queries_expected_ids_and_returns_categories():
    """
    Test that PostRepository.get_categories_by_ids:
    - Queries the database for Category objects with the given IDs.
    - Returns the expected list of Category instances.
    - Asserts db.query, query.filter, and filtered.all are called as expected.
    """
    db = Mock()
    query = Mock()
    filtered = Mock()

    expected_categories = [Mock(spec=Category), Mock(spec=Category)]

    db.query.return_value = query
    query.filter.return_value = filtered
    filtered.all.return_value = expected_categories

    repo = PostRepository(db)

    ids = [uuid4(), uuid4()]
    result = repo.get_categories_by_ids(ids)

    assert result == expected_categories
    db.query.assert_called_once_with(Category)
    query.filter.assert_called_once()
    filtered.all.assert_called_once_with()

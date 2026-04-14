from unittest.mock import Mock
from uuid import uuid4

from src.app.modules.categories.models import Category
from src.app.modules.posts.repositories import PostRepository


def test_list_uses_base_repository_defaults():
    """
    Test that PostRepository.list uses inherited BaseRepository behavior.
    """
    db = Mock()
    repo = PostRepository(db)

    query = Mock()
    paginated_query = Mock()
    expected_items = [Mock(), Mock()]
    db.query.return_value = query
    query.count.return_value = len(expected_items)
    query.limit.return_value = paginated_query
    paginated_query.offset.return_value.all.return_value = expected_items

    pagination, result_items = repo.list(limit=2, offset=0)

    assert pagination.total == 2
    assert pagination.limit == 2
    assert result_items == expected_items
    db.query.assert_called_once()
    query.count.assert_called_once_with()


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

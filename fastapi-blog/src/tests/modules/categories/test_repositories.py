from unittest.mock import Mock

from src.app.modules.categories.models import Category
from src.app.modules.categories.repositories import CategoryRepository


def test_list_delegates_to_query_all_for_category():
    """
    Test that CategoryRepository.list delegates to the correct SQLAlchemy query chain
    by calling db.query(Category) and .all(), returning the expected result.
    """
    db = Mock()
    query = Mock()
    expected_categories = [Mock(spec=Category)]

    db.query.return_value = query
    query.count.return_value = len(expected_categories)
    query.offset.return_value.all.return_value = expected_categories

    repo = CategoryRepository(db)
    _, result = repo.list()

    assert result == expected_categories
    db.query.assert_called_once_with(Category)
    query.count.assert_called_once_with()
    query.limit.assert_not_called()
    query.offset.assert_called_once_with(0)


def test_get_by_name_builds_expected_query_chain():
    """
    Test that CategoryRepository.get_by_name builds the expected SQLAlchemy query chain:
    - Calls db.query(Category)
    - Applies filter for the given name
    - Calls .first() on the filtered query
    - Returns the expected category instance
    """
    db = Mock()
    query = Mock()
    filtered = Mock()
    expected_category = Mock(spec=Category)

    db.query.return_value = query
    query.filter.return_value = filtered
    filtered.first.return_value = expected_category

    repo = CategoryRepository(db)
    result = repo.get_by_name("tech")

    assert result is expected_category
    db.query.assert_called_once_with(Category)
    query.filter.assert_called_once()
    filtered.first.assert_called_once_with()


def test_get_by_name_returns_none_when_not_found():
    db = Mock()
    query = Mock()
    filtered = Mock()

    db.query.return_value = query
    query.filter.return_value = filtered
    filtered.first.return_value = None

    repo = CategoryRepository(db)
    result = repo.get_by_name("missing")

    assert result is None
    db.query.assert_called_once_with(Category)
    query.filter.assert_called_once()
    filtered.first.assert_called_once_with()

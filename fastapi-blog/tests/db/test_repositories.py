"""
Unit tests for app.db.repositories.BaseRepository.

Uses a small concrete subclass and a mocked SQLAlchemy Session so the real
implementation (add/commit/refresh/query chain) runs and is measured by coverage.
"""

from __future__ import annotations

from unittest.mock import Mock


from app.db.repositories import BaseRepository
from app.utils.pagination import PaginationInfo


class _FakeModel:
    """Minimal model type with an `id` usable in filter(model.id == ...)."""

    id = 1


class _FakeRepo(BaseRepository[_FakeModel, int]):
    model = _FakeModel


def test_create_adds_commits_refreshes_and_returns_entity():
    """
    Test that create:
    - Adds the given entity to the session,
    - Commits the transaction,
    - Refreshes the entity,
    - Returns the entity.
    """
    db = Mock()
    repo = _FakeRepo(db)
    entity = object()

    result = repo.create(entity)

    assert result is entity
    db.add.assert_called_once_with(entity)
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(entity)


def test_get_by_id_queries_filter_one_or_none():
    """
    Test that get_by_id:
    - Queries the model from the session,
    - Applies a filter by id,
    - Returns the result of one_or_none.
    """
    db = Mock()
    query = Mock()
    filtered = Mock()
    expected = object()

    db.query.return_value = query
    query.filter.return_value = filtered
    filtered.one_or_none.return_value = expected

    repo = _FakeRepo(db)
    result = repo.get_by_id(42)

    assert result is expected
    db.query.assert_called_once_with(_FakeModel)
    query.filter.assert_called_once()
    filtered.one_or_none.assert_called_once_with()


def test_list_without_options_or_order_builds_pagination_and_items():
    """
    Test that list (with no options/order_by):
    - Calculates total count,
    - Applies limit and offset,
    - Returns correct PaginationInfo and result items.
    """
    db = Mock()
    count_query = Mock()
    count_query.count.return_value = 10

    page_query = Mock()
    limit_chain = Mock()
    page_query.limit.return_value = limit_chain
    items = [object(), object()]
    limit_chain.offset.return_value.all.return_value = items

    db.query.side_effect = [count_query, page_query]

    repo = _FakeRepo(db)
    pagination, result_items = repo.list(limit=2, offset=4)

    assert isinstance(pagination, PaginationInfo)
    assert pagination.total == 10
    assert pagination.limit == 2
    assert pagination.offset == 4
    assert pagination.hasNext is True
    assert pagination.hasPrev is True
    assert result_items == items

    assert db.query.call_count == 2
    page_query.limit.assert_called_once_with(2)
    limit_chain.offset.assert_called_once_with(4)


def test_list_with_options_and_order_by():
    """
    Test that list (with options and order_by):
    - Applies options (e.g., eager loads),
    - Applies order_by,
    - Returns correct pagination and items,
    - Calls underlying methods as expected.
    """
    db = Mock()
    count_query = Mock()
    count_query.count.return_value = 3

    page_query = Mock()
    page_query.options.return_value = page_query
    page_query.order_by.return_value = page_query
    limit_chain = Mock()
    page_query.limit.return_value = limit_chain
    limit_chain.offset.return_value.all.return_value = []

    db.query.side_effect = [count_query, page_query]

    opt = object()
    order = object()
    repo = _FakeRepo(db)
    pagination, result_items = repo.list(
        limit=5,
        offset=0,
        order_by=order,
        options=[opt],
    )

    assert pagination.total == 3
    assert result_items == []
    page_query.options.assert_called_once_with(opt)
    page_query.order_by.assert_called_once_with(order)


def test_partial_update_commits_refreshes_and_returns_entity():
    """
    Test that partial_update:
    - Commits the session,
    - Refreshes the entity,
    - Returns the entity.
    """
    db = Mock()
    repo = _FakeRepo(db)
    entity = object()

    result = repo.partial_update(entity)

    assert result is entity
    db.commit.assert_called_once_with()
    db.refresh.assert_called_once_with(entity)


def test_delete_deletes_and_commits():
    """
    Test that delete:
    - Deletes the entity from the session,
    - Commits the transaction.
    """
    db = Mock()
    repo = _FakeRepo(db)
    entity = object()

    repo.delete(entity)  # type: ignore[arg-type]

    db.delete.assert_called_once_with(entity)
    db.commit.assert_called_once_with()

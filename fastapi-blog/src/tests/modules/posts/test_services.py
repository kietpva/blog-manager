from types import SimpleNamespace
from unittest.mock import ANY, Mock
from uuid import UUID, uuid4

import pytest

from src.app.core.constants import SortOrder
from src.app.core.exceptions import NotFoundError
from src.app.modules.categories.models import Category
from src.app.modules.posts.models import Post
from src.app.modules.posts.repositories import PostRepository
from src.app.modules.posts.schemas import PostCreate, PostUpdate
from src.app.modules.posts.services import PostService
from src.app.utils.pagination import PaginationInfo


@pytest.fixture
def repo() -> Mock:
    """
    Fixture that returns a mock PostRepository object.

    This mock repository is used to isolate PostService tests from the database layer,
    enabling verification of the service logic and its interactions with repository methods.

    Returns:
        Mock: A mock instance of PostRepository.
    """
    repository = Mock(spec=PostRepository)
    repository.db = Mock()
    return repository


@pytest.fixture
def service(repo: Mock) -> PostService:
    """
    Fixture that returns a PostService instance using the provided mock repository.

    Args:
        repo (Mock): A mock instance of PostRepository.

    Returns:
        PostService: An instance of PostService with the mock repository injected.
    """
    return PostService(repo)


def make_category(name: str = "cat") -> Category:
    """
    Helper function to create a Category object with the given name.

    Args:
        name (str, optional): The name of the category. Defaults to "cat".

    Returns:
        Category: A Category instance with the specified name.
    """
    return Category(name=name)


def make_post(author_id: UUID, title: str = "t", content: str = "c") -> Post:
    """
    Helper function to create a Post object with the given author_id, title, and content.

    Args:
        author_id (UUID): The UUID of the author.
        title (str, optional): The title of the post. Defaults to "t".
        content (str, optional): The content of the post. Defaults to "c".

    Returns:
        Post: A Post instance with the specified attributes.
    """
    return Post(title=title, content=content, author_id=author_id)


def test_create_raises_not_found_when_categories_missing(
    service: PostService, repo: Mock
):
    """
    Test that PostService.create raises NotFoundException if any category_ids are missing.

    Ensures that when not all of the requested categories exist,
    the service raises the expected exception
    and that the repository's create method is not invoked.
    """
    author_id = uuid4()
    cat_ids = [uuid4(), uuid4()]

    repo.get_categories_by_ids.return_value = [make_category("cat_1")]

    payload = PostCreate(title="Post", content="Content", category_ids=cat_ids)

    with pytest.raises(NotFoundError) as exc_info:
        service.create(payload, author_id=author_id)

    assert exc_info.value.message == "One or more categories not found"
    repo.get_categories_by_ids.assert_called_once_with(cat_ids)
    repo.create.assert_not_called()


def test_create_calls_repo_create_with_constructed_post(
    service: PostService, repo: Mock
):
    """
    Test that PostService.create calls repo.create with a properly constructed Post object.

    Ensures that the returned post instance matches the attributes
    given in the payload and repository,
    and that the appropriate repository methods are called.
    """
    author_id = uuid4()
    cat_ids = [uuid4(), uuid4()]
    categories = [make_category("cat_1"), make_category("cat_2")]

    repo.get_categories_by_ids.return_value = categories
    repo.create.side_effect = lambda post: post

    payload = PostCreate(title="Post", content="Content", category_ids=cat_ids)
    result = service.create(payload, author_id=author_id)

    assert result.title == payload.title
    assert result.content == payload.content
    assert result.author_id == author_id
    assert result.categories == categories

    repo.get_categories_by_ids.assert_called_once_with(cat_ids)
    repo.create.assert_called_once()


def test_get_by_id_raises_not_found_when_missing(service: PostService, repo: Mock):
    """
    Test that PostService.get_by_id raises NotFoundException when the post does not exist.

    Ensures correct exception logic and repo method invocation for missing posts.
    """
    post_id = uuid4()
    repo.get_by_id.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        service.get_by_id(post_id)

    assert exc_info.value.message == "Post not found"
    repo.get_by_id.assert_called_once_with(post_id)


def test_get_by_id_returns_post_when_found(service: PostService, repo: Mock):
    """
    Test that PostService.get_by_id returns the post instance when found.

    Asserts the repository method is called and the found post is returned.
    """
    post_id = uuid4()
    author_id = uuid4()
    post = make_post(author_id=author_id)
    repo.get_by_id.return_value = post

    result = service.get_by_id(post_id)

    assert result is post
    repo.get_by_id.assert_called_once_with(post_id)


def test_list_returns_pagination_and_items(service: PostService, repo: Mock):
    """
    Test that PostService.list returns both pagination info and items from the repository.

    Asserts that the result matches the repository's return values, and correct arguments are used.
    """
    page = PaginationInfo(total=1, limit=10, offset=0, has_next=False, has_prev=False)
    items = [make_post(author_id=uuid4())]
    repo.list.return_value = (page, items)

    result_page, result_items = service.list(
        limit=10, offset=0, order_by=SortOrder.NEWEST
    )

    assert result_page is page
    assert result_items == items
    repo.list.assert_called_once_with(
        10, 0, order_by=SortOrder.NEWEST, search=None, options=ANY
    )


def test_partial_update_updates_title_and_categories(
    service: PostService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that PostService.partial_update correctly updates the title and categories of a post.

    Ensures:
      - Permission checking is performed.
      - Category IDs are fetched if present.
      - Partial update is performed.
      - The updated post object is returned.
    """
    post_id = uuid4()
    author_id = uuid4()
    post = make_post(author_id=author_id, title="Old", content="Old content")
    repo.get_by_id.return_value = post
    current_user = SimpleNamespace(id=uuid4())
    cat_ids = [uuid4(), uuid4()]
    categories = [make_category("cat_1"), make_category("cat_2")]
    repo.get_categories_by_ids.return_value = categories

    check_permission_mock = Mock(return_value=None)
    apply_partial_update_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.posts.services.check_permission", check_permission_mock
    )
    monkeypatch.setattr(
        "src.app.modules.posts.services.apply_partial_update", apply_partial_update_mock
    )

    payload = PostUpdate(title="New title", category_ids=cat_ids)
    expected_data = payload.model_dump(exclude_unset=True)
    expected_category_ids = expected_data.pop("category_ids", None)
    assert expected_category_ids == cat_ids

    result = service.partial_update(
        post_id=post_id, payload=payload, current_user=current_user
    )

    check_permission_mock.assert_called_once_with(
        current_user=current_user, owner_id=author_id
    )
    repo.get_categories_by_ids.assert_called_once_with(cat_ids)
    assert post.categories == categories

    apply_partial_update_mock.assert_called_once_with(instance=post, data=expected_data)
    repo.db.commit.assert_called_once_with()
    repo.db.refresh.assert_called_once_with(post)
    assert result is post


def test_partial_update_raises_not_found_when_categories_missing(
    service: PostService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that PostService.partial_update raises NotFoundException
    if provided category_ids are missing.

    Ensures permission is checked first, categories are fetched, and no update occurs if not found.
    """
    post_id = uuid4()
    author_id = uuid4()
    post = make_post(author_id=author_id)
    repo.get_by_id.return_value = post

    current_user = SimpleNamespace(id=uuid4())
    cat_ids = [uuid4(), uuid4()]
    repo.get_categories_by_ids.return_value = [make_category("cat_1")]  # missing one

    check_permission_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.posts.services.check_permission", check_permission_mock
    )

    payload = PostUpdate(category_ids=cat_ids)
    with pytest.raises(NotFoundError) as exc_info:
        service.partial_update(
            post_id=post_id, payload=payload, current_user=current_user
        )

    assert exc_info.value.message == "One or more categories not found"
    check_permission_mock.assert_called_once_with(
        current_user=current_user, owner_id=author_id
    )
    repo.get_categories_by_ids.assert_called_once_with(cat_ids)
    repo.db.commit.assert_not_called()


def test_partial_update_raises_not_found_when_post_missing(
    service: PostService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that PostService.partial_update raises NotFoundException if the target post does not exist.

    Ensures that permission, category fetch, and update are NOT called if the post is missing.
    """
    post_id = uuid4()
    repo.get_by_id.return_value = None
    current_user = SimpleNamespace(id=uuid4())

    check_permission_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.posts.services.check_permission", check_permission_mock
    )

    payload = PostUpdate(title="New title")
    with pytest.raises(NotFoundError) as exc_info:
        service.partial_update(
            post_id=post_id, payload=payload, current_user=current_user
        )

    assert exc_info.value.message == "Post not found"
    check_permission_mock.assert_not_called()
    repo.get_categories_by_ids.assert_not_called()
    repo.db.commit.assert_not_called()


def test_partial_update_without_category_ids_does_not_fetch_categories(
    service: PostService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that PostService.partial_update does NOT attempt to fetch categories
    if category_ids is not provided on the payload.

    This verifies:
      - check_permission is still called
      - repo.get_categories_by_ids is NOT called
      - apply_partial_update is called with the right data (without category_ids)
      - repo.partial_update is called with the post
      - the returned object is the post instance
    """
    post_id = uuid4()
    author_id = uuid4()
    post = make_post(author_id=author_id)
    repo.get_by_id.return_value = post
    current_user = SimpleNamespace(id=uuid4())

    check_permission_mock = Mock(return_value=None)
    apply_partial_update_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.posts.services.check_permission", check_permission_mock
    )
    monkeypatch.setattr(
        "src.app.modules.posts.services.apply_partial_update", apply_partial_update_mock
    )

    payload = PostUpdate(title="Only title")
    expected_data = payload.model_dump(exclude_unset=True)
    expected_data.pop("category_ids", None)

    result = service.partial_update(
        post_id=post_id, payload=payload, current_user=current_user
    )

    check_permission_mock.assert_called_once_with(
        current_user=current_user, owner_id=author_id
    )
    repo.get_categories_by_ids.assert_not_called()
    apply_partial_update_mock.assert_called_once_with(instance=post, data=expected_data)
    repo.db.commit.assert_called_once_with()
    repo.db.refresh.assert_called_once_with(post)
    assert result is post


def test_delete_calls_repo_delete_and_permission(
    service: PostService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that service.delete:
      - Calls check_permission with the current user and the post owner ID,
      - Calls repo.delete with the fetched post object.

    Verifies:
      - check_permission is called correctly.
      - repo.delete is called with the post.
    """
    post_id = uuid4()
    owner_id = uuid4()
    post = make_post(author_id=owner_id)
    repo.get_by_id.return_value = post

    current_user = SimpleNamespace(id=uuid4())
    check_permission_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.posts.services.check_permission", check_permission_mock
    )

    service.delete(post_id=post_id, current_user=current_user)

    check_permission_mock.assert_called_once_with(
        current_user=current_user, owner_id=owner_id
    )
    repo.delete.assert_called_once_with(post)
    repo.db.commit.assert_called_once_with()


def test_delete_raises_not_found_when_post_missing(
    service: PostService, repo: Mock, monkeypatch: pytest.MonkeyPatch
):
    """
    Test that service.delete raises NotFoundException when the target post does not exist.

    Verifies that:
      - NotFoundException is raised with the expected error message when the post is missing.
      - check_permission is not called since the post does not exist.
      - repo.delete is not called since there is nothing to delete.

    Args:
        service (PostService): The PostService instance under test.
        repo (Mock): Mocked repository.
        monkeypatch (pytest.MonkeyPatch): Pytest's monkeypatch for patching dependencies.
    """
    post_id = uuid4()
    repo.get_by_id.return_value = None

    current_user = SimpleNamespace(id=uuid4())
    check_permission_mock = Mock(return_value=None)
    monkeypatch.setattr(
        "src.app.modules.posts.services.check_permission", check_permission_mock
    )

    with pytest.raises(NotFoundError) as exc_info:
        service.delete(post_id=post_id, current_user=current_user)

    assert exc_info.value.message == "Post not found"
    check_permission_mock.assert_not_called()
    repo.delete.assert_not_called()

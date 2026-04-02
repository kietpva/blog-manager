from __future__ import annotations

from unittest.mock import Mock, call

from app import routers


def test_register_routers_includes_all_module_routers_in_order():
    """
    Test that register_routers registers all module routers on the app
    in the correct order: auth, users, posts, categories, health.
    Checks that app.include_router was called with each router.
    """
    app = Mock()

    routers.register_routers(app)

    assert app.include_router.call_args_list == [
        call(routers.auth_router),
        call(routers.users_router),
        call(routers.posts_router),
        call(routers.categories_router),
        call(routers.health_router),
    ]

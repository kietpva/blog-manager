from __future__ import annotations

from unittest.mock import Mock, call

from app import routers


def test_register_routers_includes_all_module_routers_in_order():
    """
    Test that register_routers registers all module routers on the app
    in the correct order: v1 (users/posts/categories), webhooks, health.
    Checks that app.include_router was called with each router.
    """
    app = Mock()

    routers.register_routers_api_v1(app)

    assert app.include_router.call_args_list == [
        call(routers.v1_router),
        call(routers.webhooks_router),
        call(routers.health_router),
    ]

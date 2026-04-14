from fastapi import Depends

from src.app.dependencies.auth import get_current_active_user
from src.app.dependencies.roles import require_roles
from src.app.modules.users.models import UserRole

Authenticated = Depends(get_current_active_user)
Admin = Depends(require_roles(UserRole.ADMIN))
UserOnly = Depends(require_roles(UserRole.USER))

# app/dependencies/rbac.py

from fastapi import Depends
from app.decorators.roles import require_roles
from app.dependencies.auth import get_current_active_user
from app.modules.users.models import UserRole

Authenticated = Depends(get_current_active_user)
Admin = Depends(require_roles(UserRole.admin))
UserOnly = Depends(require_roles(UserRole.user))

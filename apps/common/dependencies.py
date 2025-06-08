from fastapi import Depends, HTTPException, status
from typing import Optional # Added for CommonQueryParams

from models.user_models import User as UserModel
from models.role_models import Permission # Import the Permission enum/class
from apps.user.auth import get_current_active_user # User auth dependency

# Dependency for checking specific permissions
def requires_permission(required_permission: int):
    async def permission_checker(current_user: UserModel = Depends(get_current_active_user)):
        if not current_user.role: # Should not happen if user model is correctly populated
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User role not found.",
            )
        if not current_user.can(required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions for this action.",
            )
        return current_user
    return permission_checker

# Dependency for requiring admin privileges
def requires_admin(current_user: UserModel = Depends(get_current_active_user)):
    if not current_user.is_admin(): # is_admin() method on UserModel
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator privileges required.",
        )
    return current_user

# You can add other common dependencies here, for example:
# - Pagination parameters dependency
# - Logging dependency
# - etc.

class CommonQueryParams:
    def __init__(self, q: Optional[str] = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

# Example of how to use CommonQueryParams:
# @router.get("/")
# async def read_items(commons: CommonQueryParams = Depends()):
#     # Use commons.q, commons.skip, commons.limit
#     pass

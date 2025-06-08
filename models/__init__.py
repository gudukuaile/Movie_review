# This file can be used to make imports easier, e.g.
# from .base import Base
# from .user_models import User
# from .role_models import Role
# from .word_models import Word, Review, WordCategory
# from .category_models import Category

# For Alembic autogenerate to work well, it's often better to ensure all models
# are imported when Base.metadata is called.
# One way is to import them here, and then ensure this __init__.py is imported
# before Base.metadata.create_all() or Alembic's operations.

from .base import Base
from .role_models import Role, Permission
from .user_models import User
from .category_models import Category
from .word_models import Word, WordCategory, Review

# It's also good practice to define __all__ if you want to control 'from models import *'
__all__ = [
    "Base",
    "Role",
    "Permission",
    "User",
    "Category",
    "Word",
    "WordCategory",
    "Review",
]

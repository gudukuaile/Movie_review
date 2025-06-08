import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
from models.role_models import Role, Permission # Import Role and Permission
# Password hashing will be handled by a utility/auth service, not directly in model usually
# from werkzeug.security import generate_password_hash, check_password_hash # Will be replaced

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(128)) # Hashed password
    avatar = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    bio = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    role_id = Column(Integer, ForeignKey('roles.id'))
    role = relationship('Role', back_populates='users') # Changed from backref

    # Relationship to reviews (now associated with Word, so this might change or be removed if not directly used)
    # reviews = relationship('Review', back_populates='author')

    # __init__ logic for default role might be handled during user creation in CRUD
    # def __init__(self, **kwargs):
    #     super(User, self).__init__(**kwargs)
    #     # Default role assignment logic will move to CRUD operations

    # Methods like set_password, check_password, can, is_admin will be helpers
    # or part of an auth service / CRUD operations rather than model methods directly
    # to keep models as PURE data structures as much as possible.

    def can(self, perm: int) -> bool:
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self) -> bool:
        return self.can(Permission.ADMIN)

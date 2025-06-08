from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base
# from core.database import SessionLocal # For insert_roles, if kept in model

# Permission constants, can be moved to a dedicated core.permissions if preferred
class Permission:
    COMMENT = 1       # Corresponds to Reviewing a Word
    WORD_EDIT = 2     # Corresponds to Movie_Edit
    WORD_DELETE = 4   # Corresponds to Movie_Delete
    ADMIN = 8

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(64), unique=True, index=True)
    default = Column(Boolean, default=False, index=True)
    permissions = Column(Integer)

    users = relationship('User', back_populates='role') # Changed from backref

    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    # insert_roles might be better as a script or a startup event in FastAPI
    # For now, we'll keep the structure, but its execution needs rethinking
    @staticmethod
    def insert_roles(db_session): # Pass session explicitly
        roles_permissions = {
            'User': [Permission.COMMENT],
            'Editor': [Permission.COMMENT, Permission.WORD_EDIT],
            'Admin': [Permission.COMMENT, Permission.WORD_EDIT, Permission.WORD_DELETE, Permission.ADMIN]
        }
        default_role_name = 'User'
        for r_name, perms_list in roles_permissions.items():
            role = db_session.query(Role).filter_by(name=r_name).first()
            if role is None:
                role = Role(name=r_name)
            role.reset_permissions()
            for perm_const in perms_list:
                role.add_permission(perm_const)
            role.default = (role.name == default_role_name)
            db_session.add(role)
        db_session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions is not None and (self.permissions & perm) == perm

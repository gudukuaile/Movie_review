from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
from .base import Base
from .role_models import Permission

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(128))
    avatar = Column(String(255))
    phone = Column(String(20))
    bio = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    role_id = Column(Integer, ForeignKey('roles.id'))

    role = relationship('Role', back_populates='users')
    reviews = relationship('Review', back_populates='author')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == 'admin@example.com':
                self.role = Role.query.filter_by(name='Admin').first()
            else:
                self.role = Role.query.filter_by(default=True).first()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_admin(self):
        return self.can(Permission.ADMIN)

class AnonymousUser:
    def can(self, permissions):
        return False

    def is_admin(self):
        return False

from pydantic import BaseModel, EmailStr, constr
from typing import Optional, List
import datetime # For created_at

# Pydantic model for Role (Read-only representation)
class RoleBase(BaseModel):
    id: int
    name: str
    permissions: Optional[int] = None

class RoleRead(RoleBase):
    class Config:
        orm_mode = True

# Properties to receive via API on user creation
class UserCreate(BaseModel):
    username: constr(min_length=3, max_length=80)
    email: EmailStr
    password: constr(min_length=6) # Password will be hashed by the server
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    # role_id will be set by default or by admin, not usually by user at creation

# Properties to return to client (excluding password_hash)
class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime.datetime
    role: Optional[RoleRead] = None # Embed Role information

    class Config:
        orm_mode = True # To allow direct creation from ORM model instance

# Properties for updating a user by the user themselves
class UserUpdate(BaseModel):
    username: Optional[constr(min_length=3, max_length=80)] = None
    email: Optional[EmailStr] = None
    password: Optional[constr(min_length=6)] = None # For password change
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None

# Properties for updating a user by an admin
class UserAdminUpdate(BaseModel):
    username: Optional[constr(min_length=3, max_length=80)] = None
    email: Optional[EmailStr] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    role_id: Optional[int] = None
    password: Optional[str] = None # For admin to reset password

# Schema for Token response
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Schema for user list item (admin view)
class UserListAdmin(UserRead):
    # Could add more admin-specific fields if needed
    pass

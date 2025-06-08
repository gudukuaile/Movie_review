from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from core.config import settings
from models.user_models import User
from . import crud # Will be created later, for now direct db query or placeholder
from extend.database import get_db # To get DB session
# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# OAuth2 scheme
# tokenUrl should point to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
# Dependency to get current user
# This will be used in path operations that require authentication
async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        # token_data = schemas.TokenData(username=username) # If using TokenData schema
    except JWTError:
        raise credentials_exception

    user = crud.get_user_by_username(db, username=username) # Use CRUD function
    if user is None:
        raise credentials_exception
    return user
async def get_optional_current_user(
    db: Session = Depends(get_db), token: Optional[str] = Depends(oauth2_scheme, use_cache=False) # use_cache=False for optional
) -> Optional[User]:
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            return None # Or raise specific error for bad token if token exists
    except JWTError:
        return None # Or raise specific error for bad token if token exists
    user = crud.get_user_by_username(db, username=username) # Use CRUD function
    return user
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    # if not current_user.is_active: # Add is_active field to User model if needed
    #     raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

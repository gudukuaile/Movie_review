from fastapi import APIRouter, Depends, HTTPException, status, Body, Request
from fastapi.security import OAuth2PasswordRequestForm # For login form
from sqlalchemy.orm import Session
from typing import List, Any
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from extend.database import get_db
from models.user_models import User as UserModel # Rename to avoid clash with User schema
from models.role_models import Permission # Import Permission
from . import schemas, crud, auth # Import from current app
from apps.common import dependencies as common_deps # For common permission checks

templates = Jinja2Templates(directory="templates")
router = APIRouter(
    prefix="/users",
    tags=["Users"], # For API docs grouping
)

# --- User Authentication Routes ---

@router.post("/register", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def register_user(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user_by_email = crud.get_user_by_email(db, email=user_in.email)
    if db_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    db_user_by_username = crud.get_user_by_username(db, username=user_in.username)
    if db_user_by_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user = crud.create_user(db=db, user=user_in)
    return user

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    user = crud.get_user_by_username(db, username=form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# --- Current User Routes ---

@router.get("/me", response_model=schemas.UserRead)
async def read_users_me(current_user: UserModel = Depends(auth.get_current_active_user)):
    # current_user is already a UserModel instance from the dependency
    return current_user

@router.put("/me", response_model=schemas.UserRead)
async def update_users_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(auth.get_current_active_user),
):
    # Check for username collision if username is being changed
    if user_in.username and user_in.username != current_user.username:
        existing_user = crud.get_user_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken.")

    # Check for email collision if email is being changed
    if user_in.email and user_in.email != current_user.email:
        existing_user = crud.get_user_by_email(db, email=user_in.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered by another user.")

    updated_user = crud.update_user(db, user_id=current_user.id, user_update=user_in, current_user=current_user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found or not allowed to update.") # Should not happen if current_user is valid
    return updated_user

# --- Admin Routes for User Management ---
# These routes will require admin privileges.
# The auth.requires_permission or a specific requires_admin dependency should be used.

@router.get("/", response_model=List[schemas.UserListAdmin], dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))])
async def read_users_admin(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    # current_admin: UserModel = Depends(common_deps.requires_admin) # Example of admin check
):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))])
async def read_user_admin(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))])
async def update_user_admin(
    user_id: int,
    user_in: schemas.UserAdminUpdate,
    db: Session = Depends(get_db),
):
    db_user = crud.get_user(db, user_id=user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check for username collision if username is being changed
    if user_in.username and user_in.username != db_user.username:
        existing_user = crud.get_user_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already taken.")

    # Check for email collision if email is being changed
    if user_in.email and user_in.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user_in.email)
        if existing_user: # and existing_user.id != user_id (already handled by db_user check)
            raise HTTPException(status_code=400, detail="Email already registered by another user.")

    updated_user = crud.admin_update_user(db, user_id=user_id, user_admin_update=user_in)
    if not updated_user:
        # This might happen if role_id in user_in is invalid, crud.admin_update_user returns None
        raise HTTPException(status_code=400, detail="Failed to update user. Invalid data provided (e.g., role_id).")
    return updated_user

@router.delete("/{user_id}", response_model=schemas.UserRead, dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))])
async def delete_user_admin(user_id: int, db: Session = Depends(get_db)):
    deleted_user = crud.delete_user(db, user_id=user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user

# TODO: Add endpoint for admin to reset a user's password (part of UserAdminUpdate or separate)
# (Covered by UserAdminUpdate if password field is provided)

# TODO: Add endpoint for admin to change a user's role (covered by UserAdminUpdate)

# Placeholder for listing roles (if needed for admin UI to select roles)
@router.get("/roles/", response_model=List[schemas.RoleRead], dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))])
async def read_roles_admin(db: Session = Depends(get_db)):
    roles = crud.get_roles(db)
    return roles


@router.get("/login", name="login_page", include_in_schema=False)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/register", name="register_page", include_in_schema=False)
async def get_register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/profile", name="profile_page", include_in_schema=False)
async def get_profile_page(request: Request, current_user: UserModel = Depends(auth.get_current_active_user)):
    # In a real app, you might pre-fill a form or pass user data
    return templates.TemplateResponse("auth/profile.html", {"request": request, "current_user": current_user})


@router.get("/logout", name="logout", include_in_schema=False)
async def route_logout_and_redirect(request: Request):
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return response

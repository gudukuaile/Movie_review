from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import func # For count

from models.user_models import User, Role # Assuming Role is in user_models or imported there
from models.role_models import Permission # Import Permission if needed for logic here
from . import schemas # Import Pydantic schemas from the same app
from . import auth # Changed import for password hashing utility

# --- User CRUD ---

def get_user(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).order_by(User.id).offset(skip).limit(limit).all()

def get_users_count(db: Session) -> int:
    return db.query(func.count(User.id)).scalar()


def create_user(db: Session, user: schemas.UserCreate) -> User:
    hashed_password = auth.get_password_hash(user.password)

    # Determine user role
    # For simplicity, new users get the default 'User' role.
    # Admin creation or role assignment can be a separate process or an admin-only endpoint.
    default_role = db.query(Role).filter(Role.default == True).first()
    if not default_role:
        # Fallback or error if default role not found. This should be configured by Role.insert_roles
        # For now, let's assume it exists or handle error appropriately in a real app
        # Or, create a basic 'User' role if it doesn't exist, though this is usually seeded.
        pass # Potentially raise an error or create a default role

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        avatar=user.avatar,
        phone=user.phone,
        bio=user.bio,
        role=default_role # Assign the default role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: schemas.UserUpdate, current_user: User) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    # Ensure users can only update their own profiles unless they are admins
    # This check should ideally be in the route/dependency if it's a general rule
    if db_user.id != current_user.id and not current_user.is_admin(): # is_admin needs to be defined
        return None # Or raise HTTPException for permission denied

    update_data = user_update.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        hashed_password = auth.get_password_hash(update_data["password"])
        db_user.password_hash = hashed_password
        del update_data["password"] # Don't try to set it directly

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def admin_update_user(db: Session, user_id: int, user_admin_update: schemas.UserAdminUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None

    update_data = user_admin_update.dict(exclude_unset=True)

    if "password" in update_data and update_data["password"]:
        # Admin is resetting the password
        hashed_password = auth.get_password_hash(update_data["password"])
        db_user.password_hash = hashed_password
        del update_data["password"]

    if "role_id" in update_data:
        new_role_id = update_data["role_id"]
        role = get_role(db, new_role_id)
        if not role:
            # Handle role not found error, e.g., raise HTTPException or return error
            return None # Or specific error response
        db_user.role = role
        del update_data["role_id"]

    for field, value in update_data.items():
        setattr(db_user, field, value)

    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int) -> Optional[User]:
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user


# --- Role CRUD (Basic examples) ---

def get_role(db: Session, role_id: int) -> Optional[Role]:
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_name(db: Session, name: str) -> Optional[Role]:
    return db.query(Role).filter(Role.name == name).first()

def get_roles(db: Session, skip: int = 0, limit: int = 100) -> List[Role]:
    return db.query(Role).order_by(Role.id).offset(skip).limit(limit).all()

def create_role(db: Session, role: schemas.RoleBase) -> Role: # Assuming RoleCreate schema if needed
    # This is simplified; Role creation might be more controlled (e.g., via insert_roles)
    db_role = Role(name=role.name, permissions=role.permissions or 0)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# Static method Role.insert_roles from the model is preferred for initial seeding.
# Call it during app startup or via a CLI command.
# def initial_seed_roles(db: Session):
#    Role.insert_roles(db_session=db)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any

from extend.database import get_db
from models.user_models import User as UserModel # For auth dependency
from models.role_models import Permission # For permission check
from apps.common import dependencies as common_deps # To get auth dependencies
from . import schemas, crud # Import from current app

router = APIRouter(
    prefix="/categories",
    tags=["Categories"], # For API docs grouping
    # All routes in this router will require admin privileges
    dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))]
)

@router.post("/", response_model=schemas.CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_new_category(
    category_in: schemas.CategoryCreate,
    db: Session = Depends(get_db)
):
    existing_category = crud.get_category_by_name(db, name=category_in.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category with name '{category_in.name}' already exists.",
        )
    category = crud.create_category(db=db, category=category_in)
    return category

@router.get("/", response_model=List[schemas.CategoryRead])
async def read_all_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    categories = crud.get_categories(db, skip=skip, limit=limit)
    return categories

@router.get("/{category_id}", response_model=schemas.CategoryRead)
async def read_category_by_id(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@router.put("/{category_id}", response_model=schemas.CategoryRead)
async def update_existing_category(
    category_id: int,
    category_in: schemas.CategoryUpdate,
    db: Session = Depends(get_db)
):
    db_category = crud.get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category_in.name: # If name is being updated, check for uniqueness
        existing_category_with_new_name = crud.get_category_by_name(db, name=category_in.name)
        if existing_category_with_new_name and existing_category_with_new_name.id != category_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Another category with name '{category_in.name}' already exists.",
            )

    updated_category = crud.update_category(db, category_id=category_id, category_update=category_in)
    return updated_category


@router.delete("/{category_id}", response_model=schemas.CategoryRead)
async def delete_existing_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    # The crud.delete_category might raise an error if there are associated words,
    # depending on its implementation and DB constraints.
    # Or, we can add a check here:
    # if db_category.words and len(db_category.words) > 0: # Assuming 'words' is the relationship
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST,
    #         detail="Cannot delete category: it is currently associated with one or more words."
    #     )

    deleted_category = crud.delete_category(db, category_id=category_id)
    if not deleted_category: # Should not happen if found, unless delete_category fails internally
        raise HTTPException(status_code=500, detail="Could not delete category") # Or more specific error
    return deleted_category

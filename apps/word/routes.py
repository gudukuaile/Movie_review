from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from extend.database import get_db
from models.user_models import User as UserModel # For auth dependency
from models.role_models import Permission # For permission check
from apps.common import dependencies as common_deps # To get auth dependencies
from apps.user import auth as user_auth # To get auth dependencies
from . import schemas, crud # Import from current app

router = APIRouter(
    prefix="/words",
    tags=["Words & Reviews"], # For API docs grouping
)

# --- Public Word Routes (Listing and Detail) ---

@router.get("/", response_model=List[schemas.WordList]) # Or a paginated response schema
async def read_all_words(
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = Query(None, min_length=1, max_length=100),
    category: Optional[str] = Query(None, min_length=1, max_length=50), # Category name
    db: Session = Depends(get_db)
):
    # In a real app, you might want a dedicated paginated response schema
    # that includes total count, page number, etc.
    words = crud.get_words(db, skip=skip, limit=limit, search=search, category_name=category)
    # total_words = crud.get_words_count(db, search=search, category_name=category)
    # return {"items": words, "total": total_words, "page": skip // limit + 1, "size": limit}
    return words

@router.get("/{word_id}", response_model=schemas.WordRead)
async def read_word_detail(word_id: int, db: Session = Depends(get_db)):
    db_word = crud.get_word(db, word_id=word_id)
    if db_word is None:
        raise HTTPException(status_code=404, detail="Word not found")
    return db_word

# --- Word Management Routes (Admin Protected) ---

@router.post("/", response_model=schemas.WordRead, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(common_deps.requires_permission(Permission.WORD_EDIT))]) # Or ADMIN
async def create_new_word(
    word_in: schemas.WordCreate,
    db: Session = Depends(get_db)
    # current_user: UserModel = Depends(user_auth.get_current_active_user) # If needed for audit log etc.
):
    # Check for duplicate title if necessary, though not strictly required by original app
    # existing_word = db.query(crud.Word).filter(crud.Word.title == word_in.title).first()
    # if existing_word:
    #     raise HTTPException(status_code=400, detail="Word with this title already exists")
    word = crud.create_word(db=db, word=word_in)
    return word

@router.put("/{word_id}", response_model=schemas.WordRead,
            dependencies=[Depends(common_deps.requires_permission(Permission.WORD_EDIT))]) # Or ADMIN
async def update_existing_word(
    word_id: int,
    word_in: schemas.WordUpdate,
    db: Session = Depends(get_db)
):
    db_word = crud.get_word(db, word_id=word_id) # Check if word exists
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found")

    # Potential duplicate title check if title is being changed
    if word_in.title and word_in.title != db_word.title:
        existing_word_with_new_title = db.query(crud.Word).filter(crud.Word.title == word_in.title).first()
        if existing_word_with_new_title and existing_word_with_new_title.id != word_id :
             raise HTTPException(status_code=400, detail=f"Another word with title '{word_in.title}' already exists.")

    updated_word = crud.update_word(db, word_id=word_id, word_update=word_in)
    return updated_word

@router.delete("/{word_id}", response_model=schemas.WordRead, # Or just a status code
               dependencies=[Depends(common_deps.requires_permission(Permission.WORD_DELETE))]) # Or ADMIN
async def delete_existing_word(word_id: int, db: Session = Depends(get_db)):
    deleted_word = crud.delete_word(db, word_id=word_id)
    if not deleted_word:
        raise HTTPException(status_code=404, detail="Word not found")
    return deleted_word # Or return a success message/status

# --- Review Routes ---

@router.post("/{word_id}/reviews/", response_model=schemas.ReviewRead, status_code=status.HTTP_201_CREATED, name="create_review_for_word_api")
async def create_review_for_word(
    word_id: int,
    review_in: schemas.ReviewCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(user_auth.get_current_active_user) # Requires login
):
    db_word = crud.get_word(db, word_id=word_id) # Check if word exists
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found, cannot add review.")

    review = crud.create_review(db=db, review=review_in, word_id=word_id, user_id=current_user.id)
    return review

@router.get("/{word_id}/reviews/", response_model=List[schemas.ReviewRead])
async def get_reviews_for_word_public(
    word_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    db_word = crud.get_word(db, word_id=word_id) # Check if word exists
    if not db_word:
        raise HTTPException(status_code=404, detail="Word not found.")

    reviews = crud.get_reviews_for_word(db, word_id=word_id, skip=skip, limit=limit)
    return reviews

@router.put("/reviews/{review_id}", response_model=schemas.ReviewRead)
async def update_own_or_admin_review(
    review_id: int,
    review_in: schemas.ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(user_auth.get_current_active_user)
):
    db_review = crud.get_review(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found.")

    # Permission check is inside crud.update_review
    updated_review = crud.update_review(db, review_id=review_id, review_update=review_in, user_id=current_user.id, is_admin=current_user.is_admin())
    if not updated_review:
        raise HTTPException(status_code=403, detail="Not authorized to update this review or review not found.")
    return updated_review

@router.delete("/reviews/{review_id}", response_model=schemas.ReviewRead) # Or just status
async def delete_own_or_admin_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(user_auth.get_current_active_user)
):
    # Permission check is inside crud.delete_review
    deleted_review = crud.delete_review(db, review_id=review_id, user_id=current_user.id, is_admin=current_user.is_admin())
    if not deleted_review:
        raise HTTPException(status_code=403, detail="Not authorized to delete this review or review not found.")
    return deleted_review

# --- Admin Review Management ---
# Could be in a separate admin router or here with more specific admin checks if needed.
# For now, using the is_admin flag in the existing review update/delete.
# An explicit list for admins:
@router.get("/admin/reviews/", response_model=List[schemas.ReviewRead],
            dependencies=[Depends(common_deps.requires_permission(Permission.ADMIN))])
async def list_all_reviews_admin(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    reviews = crud.get_all_reviews_admin(db, skip=skip, limit=limit)
    # total_reviews = crud.get_reviews_count_admin(db)
    # return {"items": reviews, "total": total_reviews}
    return reviews

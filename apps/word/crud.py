from typing import Optional, List
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func

from models.word_models import Word, Review, WordCategory
from models.category_models import Category
from models.user_models import User # For review author
from . import schemas # Pydantic schemas

# --- Word CRUD ---

def get_word(db: Session, word_id: int) -> Optional[Word]:
    return (
        db.query(Word)
        .options(
            selectinload(Word.categories_association).selectinload(WordCategory.category),
            selectinload(Word.reviews).selectinload(Review.author).selectinload(User.role) # Eager load reviews and their authors + roles
        )
        .filter(Word.id == word_id)
        .first()
    )

def get_words(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    category_name: Optional[str] = None
) -> List[Word]:
    query = db.query(Word).options(
        selectinload(Word.categories_association).selectinload(WordCategory.category), # Eager load categories
        selectinload(Word.reviews) # Eager load reviews count or basic info if needed on list
    )

    if search:
        query = query.filter(Word.title.ilike(f"%{search}%")) # Case-insensitive search

    if category_name:
        query = query.join(Word.categories_association).join(WordCategory.category).filter(Category.name == category_name)

    return query.order_by(Word.created_at.desc()).offset(skip).limit(limit).all()

def get_words_count(
    db: Session,
    search: Optional[str] = None,
    category_name: Optional[str] = None
) -> int:
    query = db.query(func.count(Word.id))
    if search:
        query = query.filter(Word.title.ilike(f"%{search}%"))
    if category_name:
        query = query.join(Word.categories_association).join(WordCategory.category).filter(Category.name == category_name)
    return query.scalar()


def create_word(db: Session, word: schemas.WordCreate) -> Word:
    db_word = Word(
        title=word.title,
        img_src=word.img_src,
        rating=word.rating,
        quote=word.quote
        # created_at is default
    )
    db.add(db_word)
    db.commit() # Commit to get db_word.id for associations

    if word.category_ids:
        for cat_id in word.category_ids:
            category = db.query(Category).filter(Category.id == cat_id).first()
            if category:
                word_category_assoc = WordCategory(word_id=db_word.id, category_id=cat_id)
                db.add(word_category_assoc)
        db.commit() # Commit associations

    db.refresh(db_word)
    # Manually load categories for the returned object if WordRead schema expects them
    # This is to ensure the response model has the data after creation.
    db_word = get_word(db, db_word.id) # Reload to get populated relationships
    return db_word

def update_word(db: Session, word_id: int, word_update: schemas.WordUpdate) -> Optional[Word]:
    db_word = get_word(db, word_id) # get_word already eager loads necessary data
    if not db_word:
        return None

    update_data = word_update.dict(exclude_unset=True)

    if "category_ids" in update_data:
        new_category_ids = set(update_data.pop("category_ids", []))
        current_category_ids = {wc.category_id for wc in db_word.categories_association}

        # Remove old associations
        for wc_assoc in list(db_word.categories_association): # Iterate over a copy
            if wc_assoc.category_id not in new_category_ids:
                db.delete(wc_assoc)

        # Add new associations
        for cat_id in new_category_ids:
            if cat_id not in current_category_ids:
                category = db.query(Category).filter(Category.id == cat_id).first()
                if category: # Ensure category exists
                    new_assoc = WordCategory(word_id=db_word.id, category_id=cat_id)
                    db.add(new_assoc)

    for field, value in update_data.items():
        setattr(db_word, field, value)

    db.commit()
    db.refresh(db_word)
    # Reload to get updated relationships in the response model.
    db_word = get_word(db, db_word.id)
    return db_word

def delete_word(db: Session, word_id: int) -> Optional[Word]:
    db_word = get_word(db, word_id) # get_word eager loads associations
    if db_word:
        # Delete associations in WordCategory first
        for wc_assoc in db_word.categories_association:
            db.delete(wc_assoc)
        # Delete associated reviews
        for review_assoc in db_word.reviews:
            db.delete(review_assoc)

        db.delete(db_word) # Then delete the word itself
        db.commit()
    return db_word

# --- Review CRUD ---

def get_review(db: Session, review_id: int) -> Optional[Review]:
    return (
        db.query(Review)
        .options(selectinload(Review.author).selectinload(User.role)) # Eager load author and role
        .filter(Review.id == review_id)
        .first()
    )

def get_reviews_for_word(db: Session, word_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
    return (
        db.query(Review)
        .filter(Review.word_id == word_id)
        .options(selectinload(Review.author).selectinload(User.role)) # Eager load author and role
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_all_reviews_admin(db: Session, skip: int = 0, limit: int = 100) -> List[Review]:
    return (
        db.query(Review)
        .options(selectinload(Review.author).selectinload(User.role), selectinload(Review.word))
        .order_by(Review.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_reviews_count_admin(db: Session) -> int:
    return db.query(func.count(Review.id)).scalar()

def create_review(db: Session, review: schemas.ReviewCreate, word_id: int, user_id: int) -> Review:
    db_review = Review(
        **review.dict(),
        word_id=word_id,
        user_id=user_id
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    # Reload to populate author relationship for the response
    return get_review(db, db_review.id)


def update_review(db: Session, review_id: int, review_update: schemas.ReviewUpdate, user_id: int, is_admin: bool) -> Optional[Review]:
    db_review = get_review(db, review_id) # Eager loads author
    if not db_review:
        return None

    # Check permission: user can only update their own review, unless admin
    if not is_admin and db_review.user_id != user_id:
        return None # Or raise HTTPException for permission denied

    update_data = review_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_review, field, value)

    db.commit()
    db.refresh(db_review)
    return get_review(db, db_review.id) # Reload

def delete_review(db: Session, review_id: int, user_id: int, is_admin: bool) -> Optional[Review]:
    db_review = get_review(db, review_id) # Eager loads author
    if db_review:
        if not is_admin and db_review.user_id != user_id:
            return None # Or raise HTTPException for permission denied
        db.delete(db_review)
        db.commit()
    return db_review
